import json
import os
import uuid

import aioredis
import hashlib

from pydantic import BaseModel
from fastapi import FastAPI, Request, Response
from mq import proxy_request

app = FastAPI()

DEDUP_KEY_TTL_SECONDS = 5 * 60


class GatewayData(BaseModel):
    text: str


async def request_ratelimiter(request: Request, response: Response):
    redis = await aioredis.from_url(os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379"))

    body = await request.json()
    headers = dict(request.headers.items())
    dedup_key = f'{headers}_{body}'
    dedup_key_hashed = hashlib.sha256(dedup_key.encode('utf-8')).hexdigest()
    if await redis.get(dedup_key_hashed):
        raise Exception('Duplicate request ignored')

    await redis.set(dedup_key_hashed, 'true', ex=DEDUP_KEY_TTL_SECONDS)

    celery_task_id = str(uuid.uuid4())
    request_data = json.dumps(dict(headers=headers, body=body, task_id=celery_task_id))
    await redis.set(f'mq.proxy_request[{celery_task_id}]', request_data)
    response.headers['X-CELERY-ID'] = celery_task_id


@app.post("/")
async def gateway(request: Request, response: Response, data: GatewayData):
    try:
        await request_ratelimiter(request, response)
    except Exception as e:
        print(e)
    finally:
        return

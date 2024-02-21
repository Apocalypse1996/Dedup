import json
import os

import requests
import redis

from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.broker_connection_retry_on_startup = True
celery.conf.timezone = 'UTC'

celery.conf.beat_schedule = {
    'rate_limit_proxy_request': {
        'task': 'mq.rate_limit_proxy_request',
        'schedule': 1.0,
        'args': (8,)
    },
}


@celery.task()
def rate_limit_proxy_request(limit):
    r_ = redis.from_url(os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379"))
    keys = r_.scan_iter("mq.proxy_request*")
    limit_count = 0
    for key in keys:
        if limit_count >= limit:
            return
        limit_count += 1
        data = json.loads(r_.get(key))
        proxy_request.apply_async(kwargs=dict(headers=data['headers'], body=data['body']), task_id=data['task_id'])
        r_.delete(key)


@celery.task(bind=True)
def proxy_request(self, headers, body):
    headers['X-CELERY-ID'] = self.request.id
    response = requests.post(
        url='https://chatbot.com/webhook',
        headers=headers,
        data=body,
        timeout=5
    )
    return response.status_code

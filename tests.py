import json
import uuid
import mock

from celery.result import AsyncResult
from fastapi.testclient import TestClient
from app import app
from mq import celery

client = TestClient(app)


def test_response_always_200():
    with mock.patch('app.request_ratelimiter') as request_ratelimiter:
        request_ratelimiter.side_effect = Exception('Dummy Exception')
        response = client.post("/", content=json.dumps({'text': str(uuid.uuid4())}))
        assert response.status_code == 200


def test_request_is_queued():
    response = client.post("/", content=json.dumps({'text': str(uuid.uuid4())}))
    assert response.headers.get('X-CELERY-ID')


def test_request_is_sent():
    response = client.post("/", content=json.dumps({'text': str(uuid.uuid4())}))
    celery_task_id = response.headers.get('X-CELERY-ID')
    celery_result = AsyncResult(celery_task_id, app=celery)
    celery_result.get(timeout=5)
    assert celery_result.state == 'SUCCESS'

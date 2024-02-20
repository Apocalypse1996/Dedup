import os
import requests

from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.broker_connection_retry_on_startup = True


@celery.task(bind=True, rate_limit='8/s')
def proxy_request(self, headers, body):
    headers['X-CELERY-ID'] = self.request.id
    response = requests.post(
        url='https://chatbot.com/webhook',
        headers=headers,
        data=body,
        timeout=5
    )
    return response.status_code

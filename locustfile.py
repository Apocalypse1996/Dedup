import json
import uuid

from locust import HttpUser, task


class TestGateway(HttpUser):

    @task
    def gateway(self):
        self.client.post(
            url="/",
            data=json.dumps({'text': f"{uuid.uuid4()}"}),
            headers={'Content-Type': 'application/json'}
        )

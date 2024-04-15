from kombu.utils.url import safequote
import os
from celery import Celery
from dotenv import load_dotenv
import time

load_dotenv()

aws_access_key = safequote(os.environ.get("AWS_ACCESS_KEY_ID"))
aws_secret_key = safequote(os.environ.get("AWS_SECRET_ACCESS_KEY"))

broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)

broker_transport_options = {
    'region': os.environ.get('AWS_REGION', 'us-west-2'),
    'queue_name_prefix': 'celery-'
}

result_backend_transport_options = {
    'region': os.environ.get('AWS_REGION', 'us-west-2'),
    'table_name': 'celery_results',
}

app = Celery('tasks', broker=broker_url, backend='dynamodb://', include=['background_tasks.tasks'])
app.conf.broker_transport_options = broker_transport_options
app.conf.result_backend_transport_options = result_backend_transport_options
app.conf.broker_connection_retry_on_startup = True


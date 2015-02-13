import os
from datetime import timedelta

from kombu import Queue

from .settings import DEBUG, TIME_ZONE


# Using IronMQ when available
if os.environ.get('IRON_MQ_PROJECT_ID') and os.environ.get('IRON_MQ_TOKEN'):
    BROKER_URL = 'ironmq://%s:%s@mq-aws-eu-west-1.iron.io' % (os.environ.get('IRON_MQ_PROJECT_ID'), os.environ.get('IRON_MQ_TOKEN'))
else:
    BROKER_URL = 'amqp://guest@%s:5672' % os.environ.get('BROKER_HOST', '127.0.0.1')

BROKER_POOL_LIMIT = 128
CELERY_ACCEPT_CONTENT = ['json']  # ignore other content
CELERY_ANNOTATIONS = {
    '*': {
        'time_limit': 600.0,
    },
}
CELERY_DEFAULT_QUEUE = 'queue1'
CELERY_ENABLE_UTC = True
CELERY_RESULT_SERIALIZER = 'json'
CELERY_SEND_TASK_ERROR_EMAILS = not DEBUG
# CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379')
CELERY_TASK_RESULT_EXPIRES = 300
CELERY_TIMEZONE = TIME_ZONE
CELERY_QUEUES = (
    Queue('queue1', routing_key='email_tasks'),
)

CELERYBEAT_SCHEDULE = {
    'synchronize_email_account_scheduler': {
        'task': 'synchronize_email_account_scheduler',
        'schedule': timedelta(seconds=int(os.environ.get('EMAIL_SYNC_INTERVAL', 60))),
    },
}

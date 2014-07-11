import os
from datetime import timedelta

from kombu import Queue

from .settings import DEBUG, TIME_ZONE


# Using IronMQ when available
if os.environ.get('IRON_MQ_PROJECT_ID') and os.environ.get('IRON_MQ_TOKEN'):
    BROKER_URL = 'ironmq://%s:%s@mq-aws-eu-west-1.iron.io' % (os.environ.get('IRON_MQ_PROJECT_ID'), os.environ.get('IRON_MQ_TOKEN'))
else:
    BROKER_URL = 'amqp://guest@127.0.0.1:5672'

BROKER_POOL_LIMIT = 128
CELERY_ACCEPT_CONTENT = ['json']  # ignore other content
CELERY_ANNOTATIONS = {
    '*': {
        'time_limit': 3600.0,
    },
}
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_ENABLE_UTC = True
CELERY_RESULT_SERIALIZER = 'json'
CELERY_SEND_TASK_ERROR_EMAILS = not DEBUG
# CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_QUEUES = (
    Queue('queue1', routing_key='mailbox_scheduled-prio'),
    Queue('queue2', routing_key='mailbox_scheduled-low_prio'),
    Queue('queue3', routing_key='mailbox_manual'),
)
CELERY_ROUTES = (
    {'synchronize_email_scheduler': {  # schedule priority email tasks without interference
        'queue': 'celery'
    }},
    {'sychronize_low_priority_email': {  # schedule non-priority email tasks without interference
        'queue': 'celery'
    }},
    {'synchronize_email_flags_scheduler': {  # schedule email flags tasks without interference
        'queue': 'celery'
    }},
    {'retrieve_new_emails_for': {  # UNSEEN emails in INBOX
        'queue': 'queue1'
    }},
    {'retrieve_all_emails_for': {  # emails headers from all folders, full emails from DRAFTS
        'queue': 'queue2'
    }},
    {'retrieve_low_priority_emails_for': {  # emails not in INBOX
        'queue': 'queue2'
    }},
    {'retrieve_all_flags_for': {  # email flags from all folders, except DRAFTS
        'queue': 'queue3'
    }},
    # {'synchronize_folder': {  # email from single folder
    #     'queue': 'queue3'
    # }},
)

if DEBUG:
    CELERYBEAT_SCHEDULE = {
        'sychronize_email': {
            'task': 'synchronize_email_scheduler',
            'schedule': timedelta(seconds=12),
        },
        'sychronize_low_priority_email': {
            'task': 'synchronize_low_priority_email_scheduler',
            'schedule': timedelta(seconds=30),
        },
        'synchronize_email_flags': {
            'task': 'synchronize_email_flags_scheduler',
            'schedule': timedelta(seconds=21),
        },
    }
else:
    CELERYBEAT_SCHEDULE = {
        'sychronize_email': {
            'task': 'synchronize_email_scheduler',
            'schedule': timedelta(seconds=120),
        },
        'sychronize_low_priority_email': {
            'task': 'synchronize_low_priority_email_scheduler',
            'schedule': timedelta(seconds=300),
        },
        'synchronize_email_flags': {
            'task': 'synchronize_email_flags_scheduler',
            'schedule': timedelta(seconds=210),
        },
    }

import os
from datetime import timedelta

from celery.schedules import crontab
from kombu import Queue

from .settings import DEBUG, TIME_ZONE, REDIS_URL, TESTING

# The broker env var name to use for fetching the broker url.
BROKER_ENV = os.environ.get('BROKER_ENV', 'DEV_BROKER')
# The broker url to use, based on the env var name.
BROKER_URL = os.environ.get(BROKER_ENV, 'amqp://guest@rabbit:5672')
# The broker connection pool limit (most connections alive simultaneously).
BROKER_POOL_LIMIT = os.environ.get('BROKER_POOL_LIMIT', 64)
# The broker connection keepalive heartbeat, by default we're using TCP keep-alive instead.
BROKER_HEARTBEAT = os.environ.get('BROKER_HEARTBEAT', None)
# The broker connection timeout, may require a long timeout due to Linux DNS timeouts etc
BROKER_CONNECTION_TIMEOUT = os.environ.get('BROKER_CONNECTION_TIMEOUT', 30)

CELERY_ACCEPT_CONTENT = ['json']  # ignore other content
CELERY_ANNOTATIONS = {
    '*': {
        'time_limit': 3600.0,
    },
}
CELERY_DEFAULT_QUEUE = 'email_async_tasks'
CELERY_ENABLE_UTC = True
CELERY_RESULT_SERIALIZER = 'json'
CELERY_SEND_TASK_ERROR_EMAILS = not any([DEBUG, TESTING])
# CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_RESULT_EXPIRES = 300
CELERY_TIMEZONE = TIME_ZONE

# WARNING! When changing routes/queues, make sure you deleted them
# on the message broker to prevent routing to old queues.
CELERY_QUEUES = (
    # User initiated mutations on email like Archive, sent, move.
    Queue('email_async_tasks', routing_key='email_async_tasks'),
    # Periodic synchronization of EmailAccounts.
    Queue('email_scheduled_tasks', routing_key='email_scheduled_tasks'),
    # Initial fetch of messages.
    Queue('email_first_sync', routing_key='email_first_sync'),
    # Miscellaneous tasks.
    Queue('other_tasks', routing_key='other_tasks'),
)
CELERY_ROUTES = (
    {'synchronize_email_account_scheduler': {
        'queue': 'email_scheduled_tasks'
    }},
    {'incremental_synchronize_email_account': {
        'queue': 'email_scheduled_tasks'
    }},
    {'full_synchronize_email_account': {
        # Task created by this task, will be routed to queue3.
        'queue': 'email_scheduled_tasks'
    }},
    {'download_email_message': {
        # When task is created in first sync, this task will be routed to email_first_sync.
        'queue': 'email_scheduled_tasks'
    }},
    {'update_labels_for_message': {
        # When task is created in first sync, this task will be routed to email_first_sync.
        'queue': 'email_scheduled_tasks'
    }},
)
CELERYBEAT_SCHEDULE = {
    'synchronize_email_account_scheduler': {
        'task': 'synchronize_email_account_scheduler',
        'schedule': timedelta(seconds=int(os.environ.get('EMAIL_SYNC_INTERVAL', 60))),
    },
    'check_subscriptions_scheduler': {
        'task': 'check_subscriptions',
        'schedule': timedelta(seconds=int(os.environ.get('CHECK_SUBSCRIPTION_INTERVAL', 60 * 60 * 24))),
    },
    'synchronize_labels_scheduler': {
        'task': 'synchronize_labels_scheduler',
        'schedule': timedelta(seconds=3600),  # Once every hour.
    },
    'clear_sessions_scheduler': {
        'task': 'clear_sessions_scheduler',
        'schedule': crontab(hour=1, minute=0),  # Every night at one o'clock.
    },
    'cleanup_deleted_email_accounts_scheduler': {
        'task': 'cleanup_deleted_email_accounts',
        'schedule': crontab(hour=1, minute=0),  # Every night at one o'clock.
    },
}

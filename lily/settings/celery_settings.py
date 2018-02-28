import multiprocessing
import os

from django.conf import settings as django_settings


# The broker env var name to use for fetching the broker url.
BROKER_ENV = os.environ.get('BROKER_ENV', 'DEV_BROKER')


class CelerySettings(object):
    worker_concurrency = multiprocessing.cpu_count() * 2  # Double the amount of cpu cores as number of worker threads.
    worker_max_tasks_per_child = 10000  # After 10.000 tasks a worker is restarted.
    worker_prefetch_multiplier = 2  # Prefetch double the amount of tasks for the number of concurrent threads.

    broker_url = os.environ.get(BROKER_ENV, 'amqp://guest@rabbit:5672')  # The broker url, based on the env var name.
    broker_pool_limit = worker_concurrency * 2  # Max number of connections that can be open in the connection pool.
    # TODO: verify ssl setting on staging.
    broker_use_ssl = not django_settings.DEBUG  # Use ssl connection to the broker.

    timezone = django_settings.TIME_ZONE  # Use the django timezone.

    accept_content = ['pickle', ]  # Allow pickled content-types/serializers.

    task_compression = 'gzip'  # Use gzip compression for task messages.
    task_serializer = 'pickle'  # Use pickle to serialize tasks.
    task_always_eager = django_settings.TESTING  # If tests are run, execute tasks immediately.
    task_ignore_result = True  # Don't store results of tasks in the result backend.
    task_store_errors_even_if_ignored = False  # Also don't store errors in the result backend.
    task_track_started = False  # Don't track if a task has started already.
    task_send_sent_event = False  # Don't send an event when a task is sent to the broker.

    task_soft_time_limit = 1 * 60  # 1 minutes max execution time for tasks before soft kill.
    task_time_limit = task_soft_time_limit + 60  # +1 minutes max execution time for tasks before hard kill.

    task_default_delivery_mode = 'persistent'  # We want messages to persist even after crashes/restarts of the broker.

    # TODO: this setting is removed. Do we need to implement error mails ourselves?
    CELERY_SEND_TASK_ERROR_EMAILS = not any([django_settings.DEBUG, django_settings.TESTING])

    # TODO: fill up the schedule.
    beat_schedule = {}

    # TODO: Do we still need this?
    # task_queues = ()
    # task_routes = ()


settings = CelerySettings()


# Old stuff below.


# WARNING! When changing routes/queues, make sure you deleted them
# on the message broker to prevent routing to old queues.
# CELERY_QUEUES = (
#     # User initiated mutations on email like Archive, sent, move.
#     Queue('email_async_tasks', routing_key='email_async_tasks'),
#     # Periodic synchronization of EmailAccounts.
#     Queue('email_scheduled_tasks', routing_key='email_scheduled_tasks'),
#     # Initial fetch of messages.
#     Queue('email_first_sync', routing_key='email_first_sync'),
#     # Miscellaneous tasks.
#     Queue('other_tasks', routing_key='other_tasks'),
# )
# CELERY_ROUTES = (
#     {'synchronize_email_account_scheduler': {
#         'queue': 'email_scheduled_tasks'
#     }},
#     {'incremental_synchronize_email_account': {
#         'queue': 'email_scheduled_tasks'
#     }},
#     {'full_synchronize_email_account': {
#         # Task created by this task, will be routed to queue3.
#         'queue': 'email_scheduled_tasks'
#     }},
#     {'download_email_message': {
#         # When task is created in first sync, this task will be routed to email_first_sync.
#         'queue': 'email_scheduled_tasks'
#     }},
#     {'update_labels_for_message': {
#         # When task is created in first sync, this task will be routed to email_first_sync.
#         'queue': 'email_scheduled_tasks'
#     }},
# )
# CELERYBEAT_SCHEDULE = {
#     'synchronize_email_account_scheduler': {
#         'task': 'synchronize_email_account_scheduler',
#         'schedule': timedelta(seconds=int(os.environ.get('EMAIL_SYNC_INTERVAL', 60))),
#     },
#     'check_subscriptions_scheduler': {
#         'task': 'check_subscriptions',
#         'schedule': timedelta(seconds=int(os.environ.get('CHECK_SUBSCRIPTION_INTERVAL', 60 * 60 * 24))),
#     },
#     'synchronize_labels_scheduler': {
#         'task': 'synchronize_labels_scheduler',
#         'schedule': timedelta(seconds=3600),  # Once every hour.
#     },
#     'clear_sessions_scheduler': {
#         'task': 'clear_sessions_scheduler',
#         'schedule': crontab(hour=1, minute=0),  # Every night at one o'clock.
#     },
#     'cleanup_deleted_email_accounts_scheduler': {
#         'task': 'cleanup_deleted_email_accounts',
#         'schedule': crontab(hour=1, minute=0),  # Every night at one o'clock.
#     },
# }

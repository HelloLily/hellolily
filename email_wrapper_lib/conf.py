import os
from django.conf import settings as django_settings


def get_setting(key, default=None):
    value = getattr(django_settings, key, os.environ.get(key, default))

    if not default and not value:
        raise ValueError('{0} was not specified. Please put it in your settings or env.'.format(key))

    return value


class Settings(object):
    # Mandatory settings.
    # TODO: use the url of the package urls.py
    OAUTH2_REDIRECT_URI = get_setting('OAUTH2_REDIRECT_URI').rstrip('/')
    GOOGLE_OAUTH2_CLIENT_ID = get_setting('GOOGLE_OAUTH2_CLIENT_ID')
    GOOGLE_OAUTH2_CLIENT_SECRET = get_setting('GOOGLE_OAUTH2_CLIENT_SECRET')
    MICROSOFT_OAUTH2_CLIENT_ID = get_setting('MICROSOFT_OAUTH2_CLIENT_ID')
    MICROSOFT_OAUTH2_CLIENT_SECRET = get_setting('MICROSOFT_OAUTH2_CLIENT_SECRET')

    # Find out what to do with this.
    ADD_ACCOUNT_SUCCESS_URL = get_setting('ADD_ACCOUNT_SUCCESS_URL')

    # Optional settings.
    BATCH_SIZE = get_setting('BATCH_SIZE', 100)
    ATTACHMENT_UPLOAD_PATH = get_setting('ATTACHMENT_UPLOAD_PATH', 'email/attachments/{draft_id}/{filename}')

    # TODO: figure out way for convenient celery defaults.
    # CELERY_BROKER_URL = 'amqp://guest:guest@rabbit:5672//'
    # CELERY_TIMEZONE = 'Europe/Amsterdam'
    # CELERY_BROKER_POOL_LIMIT = 60
    # CELERY_BROKER_CONNECTION_TIMEOUT = 20
    # CELERY_ACCEPT_CONTENT = ['pickle', ]
    # CELERY_SEND_TASK_SENT_EVENT = True
    # CELERY_TRACK_STARTED = True
    # CELERYD_CONCURRENCY = 4
    # CELERYD_PREFETCH_MULTIPLIER = 2
    # CELERYD_MAX_TASKS_PER_CHILD = 1337
    # CELERY_TASK_SERIALIZER = 'pickle'
    # CELERY_MESSAGE_COMPRESSION = 'gzip'
    # CELERYD_TASK_TIME_LIMIT = 3 * 60  # 3 minutes max execution time for tasks.
    # CELERY_DEFAULT_DELIVERY_MODE = 'transient'
    # CELERY_RESULT_BACKEND = 'rpc://'
    # CELERY_RESULT_SERIALIZER = 'pickle'
    # CELERY_TASK_RESULT_EXPIRES = 5 * 60  # 5 minutes storage time for results.


settings = Settings()

import logging.config
import random
import string
from datetime import datetime, timedelta
from urlparse import urlparse, uses_netloc

import chargebee
import environ
import raven
from django.conf import global_settings
from raven.exceptions import InvalidGitRepository


root = environ.Path(__file__) - 3  # Three folders back is the root folder.
lily = environ.Path(__file__) - 2  # Two folders back is the lily folder.
env = environ.Env()  # Setup basic env to read from.
environ.Env.read_env()  # Reading .env file.


def gettext_noop(s):
    return s


def get_current_commit_sha():
    commit_sha = env.str('HEROKU_SLUG_COMMIT', default=None)
    if not commit_sha:
        try:
            commit_sha = raven.fetch_git_sha(root())
        except InvalidGitRepository:
            commit_sha = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(40))

    return commit_sha


#######################################################################################################################
# DJANGO CONFIG                                                                                                       #
#######################################################################################################################
SECRET_KEY = env.str('SECRET_KEY', default='my-secret-key')
DEBUG = env.bool('DEBUG', default=False)
SITE_ID = env.int('SITE_ID', default=1)
ADMINS = env.tuple('ADMINS', default=())
MANAGERS = ADMINS
ROOT_URLCONF = 'lily.urls'
DATABASES = {'default': env.db(default='postgres://localhost')}

#######################################################################################################################
# LILY CONFIG                                                                                                         #
#######################################################################################################################
MULTI_TENANT = env.bool('MULTI_TENANT', default=False)
REGISTRATION_POSSIBLE = env.bool('REGISTRATION_POSSIBLE', default=False)
VOIPGRID_IPS = env.str('VOIPGRID_IPS', default='127.0.0.1')
BILLING_ENABLED = env.bool('BILLING_ENABLED', default=False)
FREE_PLAN_ACCOUNT_CONTACT_LIMIT = env.int('FREE_PLAN_ACCOUNT_CONTACT_LIMIT', default=1000)
FREE_PLAN_EMAIL_ACCOUNT_LIMIT = env.int('FREE_PLAN_EMAIL_ACCOUNT_LIMIT', default=2)
CURRENT_COMMIT_SHA = get_current_commit_sha()

#######################################################################################################################
# REDIS CONFIG                                                                                                        #
#######################################################################################################################
uses_netloc.append('redis')

REDIS_ENV = env.str('REDIS_PROVIDER_ENV', default='REDIS_DEV_URL')
REDIS_URL = env.str(REDIS_ENV, default='redis://redis:6379')
REDIS = urlparse(REDIS_URL)

#######################################################################################################################
# DJANGO CHANNELS                                                                                                     #
#######################################################################################################################
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL, ],
            "channel_capacity": {
                "http.request": 200,
                "http.response*": 10,
            },
        },
        "ROUTING": "lily.routing.channel_routing",
    },
}

#######################################################################################################################
# LOCALIZATION                                                                                                        #
#######################################################################################################################
TIME_ZONE = 'Europe/Amsterdam'
DATE_INPUT_FORMATS = tuple(['%d/%m/%Y'] + list(global_settings.DATE_INPUT_FORMATS))
DATETIME_INPUT_FORMATS = tuple(['%d/%m/%Y %H:%M'] + list(global_settings.DATETIME_INPUT_FORMATS))
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('nl', gettext_noop('Dutch')),
    ('en', gettext_noop('English')),
)
USE_I18N = env.bool('USE_I18N', default=True)
USE_L10N = env.bool('USE_L10N', default=True)
USE_TZ = env.bool('USE_TZ', default=True)
FIRST_DAY_OF_WEEK = env.int('FIRST_DAY_OF_WEEK', default=1)

#######################################################################################################################
# SECURITY                                                                                                            #
#######################################################################################################################
# Automatic xss detection if the browser supports the header.
SECURE_BROWSER_XSS_FILTER = env.bool('SECURE_BROWSER_XSS_FILTER', default=False)
# Turn off browser automatically detecting content-type of files served.
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('SECURE_CONTENT_TYPE_NOSNIFF', default=False)
# Tell the browser to only connect through https for x seconds.
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
# Also include subdomains in the above setting.
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
# Redirect all pages to https.
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
# The header to use when determining if a request is made through https.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Secure csrf cookie is only sent under https connection.
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
# Show this view when csrf validation fails.
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
# Secure session cookie is only sent under https connection.
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
# Prevent client side javascript from accessing session.
SESSION_COOKIE_HTTPONLY = env.bool('SESSION_COOKIE_HTTPONLY', default=False)
# Log users out on exit of browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=False)
# Only allow iframes from our own domain, choices are DENY, SAMEORIGIN and ALLOW.
X_FRAME_OPTIONS = env.str('X_FRAME_OPTIONS', default='SAMEORIGIN')
# A list of strings representing the valid host/domain names.
ALLOWED_HOSTS = [
    'hellolily.herokuapp.com',
    'hellolily-staging.herokuapp.com',
    'app.hellolily.com',
    'localhost',
]

#######################################################################################################################
# UPLOADED MEDIA AND STATIC FILES                                                                                     #
#######################################################################################################################
if DEBUG:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

else:
    DEFAULT_FILE_STORAGE = 'lily.pipeline.filestorages.MediaFilesStorage'
    STATICFILES_STORAGE = 'lily.pipeline.filestorages.StaticFilesStorage'

COLLECTFAST_ENABLED = env.bool('COLLECTFAST_ENABLED', default=False)
COLLECTFAST_CACHE = env.str('COLLECTFAST_CACHE', default='default')

MEDIA_ROOT = env.str('MEDIA_ROOT', default=lily('files/media/'))
MEDIA_URL = env.str('MEDIA_URL', default='/media/')

STATIC_ROOT = env.str('STATIC_ROOT', default=lily('files/static/'))
STATIC_URL = env.str('STATIC_URL', default='/static/')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

ACCOUNT_LOGO_UPLOAD_TO = 'accounts/account/%(tenant_id)d/%(account_id)d/%(filename)s'

CONTACT_PICTURE_UPLOAD_TO = 'contacts/contact/%(tenant_id)d/%(contact_id)d/%(filename)s'

LILYUSER_PICTURE_UPLOAD_TO = 'users/lilyuser/%(tenant_id)d/%(user_id)d/%(filename)s'
LILYUSER_PICTURE_MAX_SIZE = env.int('MAX_AVATAR_SIZE', default=300 * 1024)

EMAIL_ATTACHMENT_UPLOAD_TO = 'messaging/email/attachments/%(tenant_id)d/%(message_id)d/%(filename)s'

EMAIL_TEMPLATE_ATTACHMENT_UPLOAD_TO = ('messaging/email/templates/attachments'
                                       '/%(tenant_id)d/%(template_id)d/%(filename)s')


STATICFILES_DIRS = (
    lily('static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY', default=None)
AWS_S3_SECURE_URLS = True
AWS_PRELOAD_METADATA = True

# custom headers for files uploaded to amazon
expires = datetime.utcnow() + timedelta(days=(25 * 365))
expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
AWS_HEADERS = {
    'Cache-Control': 'max-age=1314000',
    'Expires': expires,
}

#######################################################################################################################
# LOGIN SETTINGS                                                                                                      #
#######################################################################################################################
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'base_view'
# Also used as timeout for activation link.
PASSWORD_RESET_TIMEOUT_DAYS = env.int('PASSWORD_RESET_TIMEOUT_DAYS', default=7)
USER_INVITATION_TIMEOUT_DAYS = env.int('USER_INVITATION_TIMEOUT_DAYS', default=7)
AUTH_USER_MODEL = 'users.LilyUser'
AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',
    'lily.users.auth_backends.LilyModelBackend',
)

#######################################################################################################################
# TWO FACTOR AUTH                                                                                                     #
#######################################################################################################################
TWO_FACTOR_PATCH_ADMIN = False  # No need because we disabled it.
TWO_FACTOR_SMS_GATEWAY = 'lily.users.gateway.LilyGateway'
TWILIO_ACCOUNT_SID = env.str('TWILIO_ACCOUNT_SID', default=None)
TWILIO_AUTH_TOKEN = env.str('TWILIO_AUTH_TOKEN', default=None)
TWILIO_CALLER_ID = env.str('TWILIO_CALLER_ID', default=None)

if DEBUG:
    TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'

#######################################################################################################################
# USER SESSIONS                                                                                                       #
#######################################################################################################################
SESSION_ENGINE = 'user_sessions.backends.db'  # For http requests
CHANNEL_SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # For websocket connections
# TODO: check how to install the libmaxminddb c library on heroku.
GEOIP_PATH = lily('geoip/')

#######################################################################################################################
# MIDDLEWARE CLASSES                                                                                                  #
#######################################################################################################################
MIDDLEWARE_CLASSES = (
    # See https://docs.djangoproject.com/en/dev/ref/middleware/#middleware-ordering for ordering hints
    'django.middleware.security.SecurityMiddleware',
    'lily.middleware.SetRemoteAddrFromForwardedFor',
    # 'django.contrib.sessions.middleware.SessionMiddleware',  # Replaced by user_sessions.
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lily.middleware.TokenAuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lily.tenant.middleware.TenantMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',
)

#######################################################################################################################
# TEMPLATE SETTINGS                                                                                                   #
#######################################################################################################################
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        lily('templates/'),
    ],
    'OPTIONS': {
        'debug': DEBUG,
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            # 'django.template.context_processors.media',
            # 'django.template.context_processors.static',
            'django.template.context_processors.request',
            # 'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
        ],
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
    },
}]

if DEBUG:
    # Override the cached template loader.
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

#######################################################################################################################
# INSTALLED APPS                                                                                                      #
#######################################################################################################################
INSTALLED_APPS = (
    # Lily
    'lily',  # required for management commands
    'lily.accounts',
    'lily.billing',
    'lily.calls',
    'lily.cases',
    'lily.changes',
    'lily.contacts',
    'lily.deals',
    'lily.google',
    'lily.messaging.email',
    'lily.notes',
    'lily.parcels',
    'lily.integrations',
    'lily.provide',
    'lily.search',
    'lily.socialmedia',
    'lily.stats',
    'lily.tags',
    'lily.tenant',
    'lily.timelogs',
    'lily.users',
    'lily.utils',
    'lily.email',

    # 3rd party
    'bootstrap3',
    'django_extensions',
    'django_filters',
    'channels',
    'collectfast',
    'templated_email',
    'storages',
    'taskmonitor',
    'elasticutils',
    'timezone_field',
    'django_nose',
    'django_password_strength',
    'rest_framework',
    'rest_framework.authtoken',
    'raven.contrib.django.raven_compat',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'otp_yubikey',
    'user_sessions',  # Sessions used for http requests
    'email_wrapper_lib',
    'microsoft_mail_client',

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',  # Sessions used for websocket connections
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
)

#######################################################################################################################
# EMAIL SETTINGS                                                                                                      #
#######################################################################################################################
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# TODO: use env.email_url()

EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.host.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=25)

EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='production@email.com')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='your-password')

# Since you can't send from a different address than the user, prevent mistakes and force these to the default user.
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_PERSONAL_HOST_USER = env.str('EMAIL_PERSONAL_HOST_USER', default='lily@email.com')
EMAIL_PERSONAL_HOST_PASSWORD = env.str('EMAIL_PERSONAL_HOST_PASSWORD', default='lily-password')

BLACKLISTED_EMAIL_TAGS = [
    'audio',
    'head',
    'img',
    'iframe',
    'object',
    'script',
    'style',
    'video',
]

# django-templated-email
TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'

#######################################################################################################################
# LOGGING CONFIG                                                                                                      #
#######################################################################################################################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s <%(pathname)s#%(lineno)s %(funcName)s()>: %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
}

if DEBUG:
    LOGGING.update({
        'loggers': {
            '': {  # Everything not specified below.
                'level': 'WARNING',
                'handlers': ['console', ],
            },
            'django.security': {  # More logging specifically for security related stuff.
                'level': 'DEBUG',
                'handlers': ['console', ],
                'propagate': False,
            },
            # 'django.db': {
            #     'level': 'DEBUG',
            #     'handlers': ['console', ],
            #     'propagate': False,
            # },
            'googleapiclient': {
                'level': 'WARNING',
                'handlers': ['console', ],
                'propagate': False,
            },
            'elasticsearch.trace': {
                'level': 'DEBUG',
                'handlers': ['null', ],
                'propagate': False,
            },
            'two_factor': {
                'level': 'DEBUG',
                'handlers': ['console', ],
                'propagate': False,
            },
            'lily': {
                'level': 'DEBUG',
                'handlers': ['console', ],
                'propagate': False,
            }
        },
    })
else:
    LOGGING.update({
        'loggers': {
            '': {  # Everything not specified below.
                'level': 'ERROR',
                'handlers': ['sentry', 'mail_admins', ],
            },
            'django.security': {  # More logging specifically for security related stuff.
                'level': 'INFO',
                'handlers': ['sentry', ],
                'propagate': False,
            },
            'raven': {  # Logging for Raven and all submodules.
                'level': 'INFO',
                'handlers': ['console', ],
                'propagate': False,
            },
            'sentry': {  # Logging for Sentry and all submodules.
                'level': 'INFO',
                'handlers': ['console', ],
                'propagate': False,
            },
            'elasticsearch.trace': {
                'level': 'DEBUG',
                'handlers': ['null', ],
                'propagate': False,
            },
            'lily': {
                'level': 'DEBUG',
                'handlers': ['console', ],
                'propagate': True,
            }
        },
    })

# Disable default logging and use only our own.
LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)

#######################################################################################################################
# CACHING CONFIG                                                                                                      #
#######################################################################################################################

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    # TODO: use env.cache_url?

    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (REDIS.hostname, REDIS.port),
            'TIMEOUT': 300,  # Default django value of 5 minutes
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': REDIS.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
        'staticfiles': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (REDIS.hostname, REDIS.port),
            'TIMEOUT': None,
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': REDIS.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
        'collectfast': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (REDIS.hostname, REDIS.port),
            'TIMEOUT': 900,  # 15 minutes should be enough for upload to amazon
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': REDIS.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
    }

#######################################################################################################################
# ELASTICSEARCH                                                                                                       #
#######################################################################################################################
# Set this property to true to run without a local Elasticsearch.
ES_DISABLED = env.bool('ES_DISABLED', default=False)

# The location of the Elasticsearch cluster. The following really sucks:
# ES supports two ways of configuring urls; by string and by dict, however:
# Urls with authentication can only be done with dict method, which ElasticUtils
# does not support directly, but we can make it work with a small workaround.
# (ElasticUtils expects it to be be hashable, which does not work with dict so we use a tuple).


def es_url_to_dict(url):
    parse = urlparse(url)
    port = parse.port if parse.port else (80 if parse.scheme == 'http' else 443)
    use_ssl = port is 443
    host = {'host': parse.hostname,
            'port': port,
            'use_ssl': use_ssl,
            'http_auth': '%s:%s' % (parse.username, parse.password)}
    return tuple(sorted(host.items()))


ES_PROVIDER_ENV = env.str('ES_PROVIDER_ENV', default='ES_DEV_URL')
ES_URLS = [es_url_to_dict(env.str(ES_PROVIDER_ENV, default='http://es:9200'))]

# The index Elasticsearch uses (as a prefix).
ES_INDEXES = {'default': 'main_index'}

# Default timeout of elasticsearch is to0 short for bulk updating, so we extend the timeout.
ES_TIMEOUT = env.int('ES_TIMEOUT', default=20)  # Default is 5
ES_MAXSIZE = env.int('ES_MAXSIZE', default=2)  # Default is 10
ES_BLOCK = env.bool('ES_BLOCK', default=True)  # Default is False

#######################################################################################################################
# Gmail settings                                                                                                  #
#######################################################################################################################
GOOGLE_OAUTH2_CLIENT_ID = env.str('GOOGLE_OAUTH2_CLIENT_ID', default='')
GOOGLE_OAUTH2_CLIENT_SECRET = env.str('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
GMAIL_FULL_MESSAGE_BATCH_SIZE = env.int('GMAIL_FULL_MESSAGE_BATCH_SIZE', default=300)
GMAIL_LABEL_UPDATE_BATCH_SIZE = env.int('GMAIL_LABEL_UPDATE_BATCH_SIZE', default=500)
GMAIL_PARTIAL_SYNC_LIMIT = env.int('GMAIL_PARTIAL_SYNC_LIMIT', default=899)
GMAIL_CALLBACK_URL = env.str('GMAIL_CALLBACK_URL', default='http://localhost:8000/messaging/email/callback/')
GMAIL_SYNC_DELAY_INTERVAL = 1
GMAIL_SYNC_LOCK_LIFETIME = 300
# A chuck size of -1 indicates that the entire file should be uploaded in a single request. If the underlying platform
# supports streams, such as Python 2.6 or later, then this can be very efficient as it avoids multiple connections, and
# also avoids loading the entire file into memory before sending it.
GMAIL_CHUNK_SIZE = -1
# Disable resumable uploads.
# https://developers.google.com/api-client-library/python/guide/media_upload#resumable-media-chunked-upload
# With resumable uploads enabled, tests on sending email behave different when mocking. In the old situation resumable
# was enabled but code handling failing uploads was missing.
GMAIL_UPLOAD_RESUMABLE = False
GMAIL_LABEL_INBOX = env.str('GMAIL_LABEL_INBOX', default='INBOX')
GMAIL_LABEL_SPAM = env.str('GMAIL_LABEL_SPAM', default='SPAM')
GMAIL_LABEL_TRASH = env.str('GMAIL_LABEL_TRASH', default='TRASH')
GMAIL_LABEL_UNREAD = env.str('GMAIL_LABEL_UNREAD', default='UNREAD')
GMAIL_LABEL_STAR = env.str('GMAIL_LABEL_STAR', default='STARRED')
GMAIL_LABEL_IMPORTANT = env.str('GMAIL_LABEL_IMPORTANT', default='IMPORTANT')
GMAIL_LABEL_SENT = env.str('GMAIL_LABEL_SENT', default='SENT')
GMAIL_LABEL_DRAFT = env.str('GMAIL_LABEL_DRAFT', default='DRAFT')
GMAIL_LABEL_CHAT = env.str('GMAIL_LABEL_CHAT', default='CHAT')
GMAIL_LABEL_PERSONAL = env.str('GMAIL_LABEL_PERSONAL', default='CATEGORY_PERSONAL')
GMAIL_LABELS_DONT_MANIPULATE = [GMAIL_LABEL_UNREAD, GMAIL_LABEL_STAR, GMAIL_LABEL_IMPORTANT, GMAIL_LABEL_SENT,
                                GMAIL_LABEL_DRAFT, GMAIL_LABEL_CHAT]
MAX_SYNC_FAILURES = 3

#######################################################################################################################
# Django rest settings                                                                                                #
#######################################################################################################################
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # Authenticate with multiple classes and set the tenant user afterwards.
        # If you want to add another authentication option, do it in this class instead of here.
        'lily.api.drf_extensions.authentication.LilyApiAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_METADATA_CLASS': 'lily.api.drf_extensions.metadata.CustomMetaData',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',  # Use application/json instead of multipart/form-data requests in tests.
    'DEFAULT_PAGINATION_CLASS': 'lily.api.drf_extensions.pagination.CustomPagination',
}

#######################################################################################################################
# External app settings                                                                                               #
#######################################################################################################################
DATAPROVIDER_API_KEY = env.str('DATAPROVIDER_API_KEY', default=None)
DATAPROVIDER_API_URL = 'https://www.dataprovider.com/api/3.0/lookup/hostname.json'

INTERCOM_APP_ID = env.str('INTERCOM_APP_ID', default='')
INTERCOM_KEY = env.str('INTERCOM_KEY', default='')
INTERCOM_HMAC_SECRET = env.str('INTERCOM_HMAC_SECRET', default='')

# Sentry & Raven
SENTRY_BACKEND_DSN = env.str('SENTRY_BACKEND_DSN', default='')
SENTRY_BACKEND_PUBLIC_DSN = env.str('SENTRY_BACKEND_PUBLIC_DSN', default='')
SENTRY_FRONTEND_DSN = env.str('SENTRY_FRONTEND_DSN', default='')
SENTRY_FRONTEND_PUBLIC_DSN = env.str('SENTRY_FRONTEND_PUBLIC_DSN', default='')
RAVEN_CONFIG = {
    'dsn': SENTRY_BACKEND_DSN,
    'release': CURRENT_COMMIT_SHA,
}

CHARGEBEE_API_KEY = env.str('CHARGEBEE_API_KEY', default='')
CHARGEBEE_SITE = env.str('CHARGEBEE_SITE', default='hellolily-test')
CHARGEBEE_FREE_PLAN_NAME = env.str('CHARGEBEE_FREE_PLAN_NAME', default='lily-personal')
CHARGEBEE_TEAM_PLAN_NAME = env.str('CHARGEBEE_TEAM_PLAN_NAME', default='lily-team')
CHARGEBEE_PRO_PLAN_NAME = env.str('CHARGEBEE_PRO_PLAN_NAME', default='lily-professional')
CHARGEBEE_PRO_TRIAL_PLAN_NAME = env.str('CHARGEBEE_PRO_TRIAL_PLAN_NAME', default='lily-professional-trial')

chargebee.configure(CHARGEBEE_API_KEY, CHARGEBEE_SITE)

# Client ID and secret for the Lily Slack app.
SLACK_LILY_CLIENT_ID = env.str('SLACK_LILY_CLIENT_ID', default='')
SLACK_LILY_CLIENT_SECRET = env.str('SLACK_LILY_CLIENT_SECRET', default='')
# Token used to verify requests are actually coming from Slack.
SLACK_LILY_TOKEN = env.str('SLACK_LILY_TOKEN', default='')

#######################################################################################################################
# TESTING                                                                                                             #
#######################################################################################################################
TEST_RUNNER = 'lily.tests.runner.LilyNoseTestSuiteRunner'
NOSE_ARGS = ['--nocapture', '--nologcapture', '--verbosity=3']
TESTING = False  # Is set to True in the testrunner.
TEST_SUPPRESS_LOG = True

#######################################################################################################################
# EMAIL WRAPPER LIB                                                                                                   #
#######################################################################################################################
OAUTH2_REDIRECT_URI = env.str('OAUTH2_REDIRECT_URI', default='')
GOOGLE_OAUTH2_CLIENT_ID = env.str('GOOGLE_OAUTH2_CLIENT_ID', default='')
GOOGLE_OAUTH2_CLIENT_SECRET = env.str('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
MICROSOFT_OAUTH2_CLIENT_ID = env.str('MICROSOFT_OAUTH2_CLIENT_ID', default='')
MICROSOFT_OAUTH2_CLIENT_SECRET = env.str('MICROSOFT_OAUTH2_CLIENT_SECRET', default='')

ADD_ACCOUNT_SUCCESS_URL = env.str('ADD_ACCOUNT_SUCCESS_URL', default='email_v3_homeview')

BATCH_SIZE = env.str('BATCH_SIZE', default=100)
ATTACHMENT_UPLOAD_PATH = env.str('ATTACHMENT_UPLOAD_PATH', default='email/attachments/{draft_id}/{filename}')

#######################################################################################################################
# MISCELLANEOUS SETTINGS                                                                                              #
#######################################################################################################################
# TODO: These settings can be removed once all forms are converted to Angular
BOOTSTRAP3 = {
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4',
    'set_required': False,
}

SHELL_PLUS_POST_IMPORTS = (
    ('django.db', 'connection'),
    ('django.db', 'reset_queries'),
    ('pprint', 'pprint'),
    ('django.utils.translation', 'activate'),
    ('django.utils.translation', 'get_language'),
    ('lily.accounts.factories', '*'),
    ('lily.calls.factories', '*'),
    ('lily.cases.factories', '*'),
    ('lily.contacts.factories', '*'),
    ('lily.deals.factories', '*'),
    ('lily.notes.factories', '*'),
    ('lily.tags.factories', '*'),
    ('lily.tenant.factories', '*'),
    ('lily.users.factories', '*'),
)

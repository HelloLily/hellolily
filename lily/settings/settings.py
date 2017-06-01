import logging.config
import os
import random
import string
from datetime import datetime, timedelta
from urlparse import urlparse, uses_netloc

import chargebee
import dj_database_url
import raven
from django.conf import global_settings
from django.core.urlresolvers import reverse_lazy


#######################################################################################################################
# MISCELLANEOUS SETTINGS                                                                                              #
#######################################################################################################################
# Provide a dummy translation function without importing it from
# django.utils.translation, because that module is depending on
# settings itself possibly resulting in a circular import
from raven.exceptions import InvalidGitRepository


def gettext_noop(s):
    return s


# Turn 0 or 1 into False/True respectively
def boolean(value):
    return bool(int(value))


# Get local path for any given folder/path
def local_path(path):
    return os.path.join(os.path.dirname(__file__), os.pardir, path)


# Don't share this with anybody
SECRET_KEY = os.environ.get('SECRET_KEY', 'my-secret-key')

# Current git commit hash
CURRENT_COMMIT_SHA = os.environ.get('HEROKU_SLUG_COMMIT')

if not CURRENT_COMMIT_SHA:
    try:
        CURRENT_COMMIT_SHA = raven.fetch_git_sha(os.path.dirname(os.pardir))
    except InvalidGitRepository:
        CURRENT_COMMIT_SHA = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(40))

#######################################################################################################################
# DJANGO CONFIG                                                                                                       #
#######################################################################################################################
# Try to read as much configuration from ENV
DEBUG = boolean(os.environ.get('DEBUG', 0))
TESTING = False

ADMINS = eval(os.environ.get('ADMINS', '()'))
MANAGERS = ADMINS

# Main urls file
ROOT_URLCONF = 'lily.urls'

# Database connection settings
DATABASES = {
    'default': dj_database_url.config(default='postgres://localhost')
}

SITE_ID = os.environ.get('SITE_ID', 1)

#######################################################################################################################
# REDIS CONFIG                                                                                                        #
#######################################################################################################################
uses_netloc.append('redis')

REDIS_ENV = os.environ.get('REDIS_PROVIDER_ENV', 'REDIS_DEV_URL')
REDIS_URL = os.environ.get(REDIS_ENV, 'redis://redis:6379')
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
USE_I18N = boolean(os.environ.get('USE_I18N', 1))
USE_L10N = boolean(os.environ.get('USE_L10N', 1))
USE_TZ = boolean(os.environ.get('USE_TZ', 1))
FIRST_DAY_OF_WEEK = os.environ.get('FIRST_DAY_OF_WEEK', 1)

#######################################################################################################################
# SECURITY                                                                                                            #
#######################################################################################################################
# Automatic xss detection if the browser supports the header.
SECURE_BROWSER_XSS_FILTER = boolean(os.environ.get('SECURE_BROWSER_XSS_FILTER', 0))
# Turn off browser automatically detecting content-type of files served.
SECURE_CONTENT_TYPE_NOSNIFF = boolean(os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF', 0))
# Tell the browser to only connect through https for x seconds.
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 0))
# Also include subdomains in the above setting.
SECURE_HSTS_INCLUDE_SUBDOMAINS = boolean(os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 0))
# Redirect all pages to https.
SECURE_SSL_REDIRECT = boolean(os.environ.get('SECURE_SSL_REDIRECT', 0))
# The header to use when determining if a request is made through https.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Secure csrf cookie is only sent under https connection.
CSRF_COOKIE_SECURE = boolean(os.environ.get('CSRF_COOKIE_SECURE', 0))
# Show this view when csrf validation fails.
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
# Secure session cookie is only sent under https connection.
SESSION_COOKIE_SECURE = boolean(os.environ.get('SESSION_COOKIE_SECURE', 0))
# Prevent client side javascript from accessing session.
SESSION_COOKIE_HTTPONLY = boolean(os.environ.get('SESSION_COOKIE_HTTPONLY', 0))
# Log users out on exit of browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = boolean(os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', 0))
# Only allow iframes from our own domain, choices are DENY, SAMEORIGIN and ALLOW.
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'SAMEORIGIN')
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

COLLECTFAST_ENABLED = boolean(os.environ.get('COLLECTFAST_ENABLED', 0))
COLLECTFAST_CACHE = os.environ.get('COLLECTFAST_CACHE', 'default')

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', local_path('files/media/'))
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

STATIC_ROOT = os.environ.get('STATIC_ROOT', local_path('files/static/'))
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

ACCOUNT_LOGO_UPLOAD_TO = 'accounts/account/%(tenant_id)d/%(account_id)d/%(filename)s'

CONTACT_PICTURE_UPLOAD_TO = 'contacts/contact/%(tenant_id)d/%(contact_id)d/%(filename)s'

LILYUSER_PICTURE_UPLOAD_TO = 'users/lilyuser/%(tenant_id)d/%(user_id)d/%(filename)s'
LILYUSER_PICTURE_MAX_SIZE = os.environ.get('MAX_AVATAR_SIZE', 300 * 1024)

EMAIL_ATTACHMENT_UPLOAD_TO = 'messaging/email/attachments/%(tenant_id)d/%(message_id)d/%(filename)s'

EMAIL_TEMPLATE_ATTACHMENT_UPLOAD_TO = ('messaging/email/templates/attachments'
                                       '/%(tenant_id)d/%(template_id)d/%(filename)s')


STATICFILES_DIRS = (
    local_path('static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
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
LOGOUT_URL = reverse_lazy('logout')
# Also used as timeout for activation link.
PASSWORD_RESET_TIMEOUT_DAYS = os.environ.get('PASSWORD_RESET_TIMEOUT_DAYS', 7)
USER_INVITATION_TIMEOUT_DAYS = int(os.environ.get('USER_INVITATION_TIMEOUT_DAYS', 7))
AUTH_USER_MODEL = 'users.LilyUser'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

#######################################################################################################################
# TWO FACTOR AUTH                                                                                                     #
#######################################################################################################################
TWO_FACTOR_PATCH_ADMIN = False  # No need because we disabled it.
TWO_FACTOR_SMS_GATEWAY = 'lily.users.gateway.LilyGateway'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_CALLER_ID = os.environ.get('TWILIO_CALLER_ID')

if DEBUG:
    TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'

#######################################################################################################################
# USER SESSIONS                                                                                                       #
#######################################################################################################################
SESSION_ENGINE = 'user_sessions.backends.db'  # For http requests
CHANNEL_SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # For websocket connections

#######################################################################################################################
# USER SESSIONS                                                                                                       #
#######################################################################################################################
# TODO: check how to install the libmaxminddb c library on heroku.
GEOIP_PATH = local_path('geoip/')

#######################################################################################################################
# MIDDLEWARE CLASSES                                                                                                  #
#######################################################################################################################
MIDDLEWARE_CLASSES = (
    # See https://docs.djangoproject.com/en/dev/ref/middleware/#middleware-ordering for ordering hints
    'django.middleware.security.SecurityMiddleware',
    'lily.middleware.SetRemoteAddrFromForwardedFor',
    # 'django.contrib.sessions.middleware.SessionMiddleware',  # Replaced by user_sessions.
    'user_sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
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
        local_path('templates/'),
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

EMAIL_USE_TLS = boolean(os.environ.get('EMAIL_USE_TLS', 0))
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.host.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'production@email.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-password')

# Since you can't send from a different address than the user, prevent mistakes and force these to the default user.
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_PERSONAL_HOST_USER = os.environ.get('EMAIL_PERSONAL_HOST_USER', 'lily@email.com')
EMAIL_PERSONAL_HOST_PASSWORD = os.environ.get('EMAIL_PERSONAL_HOST_PASSWORD', 'lily-password')

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
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'null': {
            'class': 'django.utils.log.NullHandler',
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
            'elasticsearch.trace': {
                'level': 'DEBUG',
                'handlers': ['null', ],
                'propagate': False,
            },
            'two_factor': {
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
                'handlers': ['sentry', ],
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
# SUBSCRIPTION LIMITS                                                                                                 #
#######################################################################################################################
# Limits for the free plan.
FREE_PLAN_ACCOUNT_CONTACT_LIMIT = os.environ.get('FREE_PLAN_ACCOUNT_CONTACT_LIMIT', 1000)
FREE_PLAN_EMAIL_ACCOUNT_LIMIT = os.environ.get('FREE_PLAN_EMAIL_ACCOUNT_LIMIT', 2)

#######################################################################################################################
# ELASTICSEARCH                                                                                                       #
#######################################################################################################################
# Set this property to true to run without a local Elasticsearch.
ES_DISABLED = boolean(os.environ.get('ES_DISABLED', 0))

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


ES_PROVIDER_ENV = os.environ.get('ES_PROVIDER_ENV', 'ES_DEV_URL')
ES_URLS = [es_url_to_dict(os.environ.get(ES_PROVIDER_ENV, 'http://es:9200'))]

# The index Elasticsearch uses (as a prefix).
ES_INDEXES = {'default': 'main_index'}

# Default timeout of elasticsearch is to short for bulk updating, so we extend te timeout
ES_TIMEOUT = os.environ.get('ES_TIMEOUT', 20)  # Default is 5

ES_MAXSIZE = os.environ.get('ES_MAXSIZE', 2)  # Default is 10

ES_BLOCK = os.environ.get('ES_BLOCK', True)  # Default is False

#######################################################################################################################
# Gmail settings                                                                                                  #
#######################################################################################################################
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID', '')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET', '')
GMAIL_FULL_MESSAGE_BATCH_SIZE = os.environ.get('GMAIL_FULL_MESSAGE_BATCH_SIZE', 300)
GMAIL_LABEL_UPDATE_BATCH_SIZE = os.environ.get('GMAIL_LABEL_UPDATE_BATCH_SIZE', 500)
GMAIL_PARTIAL_SYNC_LIMIT = os.environ.get('GMAIL_PARTIAL_SYNC_LIMIT', 899)
GMAIL_CALLBACK_URL = os.environ.get('GMAIL_CALLBACK_URL', 'http://localhost:8000/messaging/email/callback/')
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
GMAIL_LABEL_INBOX = os.environ.get('GMAIL_LABEL_INBOX', 'INBOX')
GMAIL_LABEL_SPAM = os.environ.get('GMAIL_LABEL_SPAM', 'SPAM')
GMAIL_LABEL_TRASH = os.environ.get('GMAIL_LABEL_TRASH', 'TRASH')
GMAIL_LABEL_UNREAD = os.environ.get('GMAIL_LABEL_UNREAD', 'UNREAD')
GMAIL_LABEL_STAR = os.environ.get('GMAIL_LABEL_STAR', 'STARRED')
GMAIL_LABEL_IMPORTANT = os.environ.get('GMAIL_LABEL_IMPORTANT', 'IMPORTANT')
GMAIL_LABEL_SENT = os.environ.get('GMAIL_LABEL_SENT', 'SENT')
GMAIL_LABEL_DRAFT = os.environ.get('GMAIL_LABEL_DRAFT', 'DRAFT')
GMAIL_LABEL_CHAT = os.environ.get('GMAIL_LABEL_CHAT', 'CHAT')
GMAIL_LABEL_PERSONAL = os.environ.get('GMAIL_LABEL_PERSONAL', 'CATEGORY_PERSONAL')
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
DATAPROVIDER_API_KEY = os.environ.get('DATAPROVIDER_API_KEY')
DATAPROVIDER_API_URL = 'https://www.dataprovider.com/api/0.1/lookup/hostname.json'

INTERCOM_APP_ID = os.environ.get('INTERCOM_APP_ID', '')
INTERCOM_KEY = os.environ.get('INTERCOM_KEY', '')
INTERCOM_HMAC_SECRET = os.environ.get('INTERCOM_HMAC_SECRET', '')

# Sentry & Raven
SENTRY_BACKEND_DSN = os.environ.get('SENTRY_BACKEND_DSN', '')
SENTRY_BACKEND_PUBLIC_DSN = os.environ.get('SENTRY_BACKEND_PUBLIC_DSN', '')
SENTRY_FRONTEND_DSN = os.environ.get('SENTRY_FRONTEND_DSN', '')
SENTRY_FRONTEND_PUBLIC_DSN = os.environ.get('SENTRY_FRONTEND_PUBLIC_DSN', '')
RAVEN_CONFIG = {
    'dsn': SENTRY_BACKEND_DSN,
    'release': CURRENT_COMMIT_SHA,
}

CHARGEBEE_API_KEY = os.environ.get('CHARGEBEE_API_KEY', '')
CHARGEBEE_SITE = os.environ.get('CHARGEBEE_SITE', 'hellolily-test')
CHARGEBEE_FREE_PLAN_NAME = os.environ.get('CHARGEBEE_FREE_PLAN_NAME', 'lily-personal')
CHARGEBEE_TEAM_PLAN_NAME = os.environ.get('CHARGEBEE_TEAM_PLAN_NAME', 'lily-team')
CHARGEBEE_PRO_PLAN_NAME = os.environ.get('CHARGEBEE_PRO_PLAN_NAME', 'lily-professional')
CHARGEBEE_PRO_TRIAL_PLAN_NAME = os.environ.get('CHARGEBEE_PRO_TRIAL_PLAN_NAME', 'lily-professional-trial')

chargebee.configure(CHARGEBEE_API_KEY, CHARGEBEE_SITE)

# Client ID and secret for the Lily Slack app.
SLACK_LILY_CLIENT_ID = os.environ.get('SLACK_LILY_CLIENT_ID', '')
SLACK_LILY_CLIENT_SECRET = os.environ.get('SLACK_LILY_CLIENT_SECRET', '')
# Token used to verify requests are actually coming from Slack.
SLACK_LILY_TOKEN = os.environ.get('SLACK_LILY_TOKEN', '')

#######################################################################################################################
# TESTING                                                                                                             #
#######################################################################################################################
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--nocapture', '--nologcapture', '--verbosity=3']

#######################################################################################################################
# MISCELLANEOUS SETTINGS                                                                                              #
#######################################################################################################################
# Registration form
REGISTRATION_POSSIBLE = boolean(os.environ.get('REGISTRATION_POSSIBLE', 0))

# Messaging framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# Tenant support
MULTI_TENANT = boolean(os.environ.get('MULTI_TENANT', 0))

BILLING_ENABLED = boolean(os.environ.get('BILLING_ENABLED', 0))

# Django Bootstrap
# TODO: These settings can be removed once all forms are converted to Angular
BOOTSTRAP3 = {
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4',
    'set_required': False,
}

VOIPGRID_IPS = os.environ.get('VOIPGRID_IPS', '127.0.0.1')

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

from .celeryconfig import *  # noqa

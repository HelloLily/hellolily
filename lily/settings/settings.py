import os
from datetime import datetime, timedelta
from urlparse import urlparse, uses_netloc

from django.conf import global_settings
from django.core.urlresolvers import reverse_lazy

import dj_database_url


#######################################################################################################################
# MISCELLANEOUS SETTINGS                                                                                              #
#######################################################################################################################
# Provide a dummy translation function without importing it from
# django.utils.translation, because that module is depending on
# settings itself possibly resulting in a circular import
gettext_noop = lambda s: s

# Don't share this with anybody
SECRET_KEY = os.environ.get('SECRET_KEY', 'my-secret-key')

# Register database scheme and redis caching in URLs
uses_netloc.append('postgres')
uses_netloc.append('redis')

# Turn 0 or 1 into False/True respectively
boolean = lambda value: bool(int(value))

# Get local path for any given folder/path
local_path = lambda path: os.path.join(os.path.dirname(__file__), os.pardir, path)

#######################################################################################################################
# DJANGO CONFIG                                                                                                       #
#######################################################################################################################
# Try to read as much configuration from ENV
DEBUG = boolean(os.environ.get('DEBUG', 0))
TEMPLATE_DEBUG = boolean(os.environ.get('DEBUG', DEBUG))

ADMINS = eval(os.environ.get('ADMINS', '()'))
MANAGERS = ADMINS

# Main urls file
ROOT_URLCONF = 'lily.urls'

# WSGI setting
WSGI_APPLICATION = 'lily.wsgi.application'

# Database connection settings
DATABASES = {
    'default': dj_database_url.config(default='postgres://localhost')
}

# Make unaccented search possible on db.
DATABASES['default']['ENGINE'] = 'lily.db.backends.unaccent_postgresql_psycopg2'
SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

SITE_ID = os.environ.get('SITE_ID', 1)

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
# Secure csrf cookie is only sent under https connection, for production this needs to be set to True
CSRF_COOKIE_SECURE = boolean(os.environ.get('CSRF_COOKIE_SECURE', 0))
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
# Secure session cookie is only sent under https connection, for production this needs to be set to True
SESSION_COOKIE_SECURE = boolean(os.environ.get('SESSION_COOKIE_SECURE', 0))
# Prevent client side javascript from accessing session, for production this needs to be set to True
SESSION_COOKIE_HTTPONLY = boolean(os.environ.get('SESSION_COOKIE_HTTPONLY', 0))
SESSION_EXPIRE_AT_BROWSER_CLOSE = boolean(os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', 0))
# Only allow iframes from our own domain, for production this needs to be set to DENY
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'SAMEORIGIN')
ALLOWED_HOSTS = [
    'hellolily.herokuapp.com',
    'app.hellolily.com',
    'app.hellolily.nl',
    'app.hellolilly.nl',
    'localhost',
]

#######################################################################################################################
# UPLOADED MEDIA AND STATIC FILES                                                                                     #
#######################################################################################################################
if DEBUG:
    JQUERY_URL = ''  # Debug toolbar
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

else:
    DEFAULT_FILE_STORAGE = 'lily.pipeline.filestorages.MediaFilesStorage'
    STATICFILES_STORAGE = 'lily.pipeline.filestorages.StaticFilesStorage'

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', local_path('files/media/'))
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

STATIC_ROOT = os.environ.get('STATIC_ROOT', local_path('files/static/'))
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

ACCOUNT_UPLOAD_TO = 'images/profile/account'
CONTACT_UPLOAD_TO = 'images/profile/contact'
EMAIL_ATTACHMENT_UPLOAD_TO = 'messaging/email/attachments/%(tenant_id)d/%(message_id)d/%(filename)s'
EMAIL_TEMPLATE_ATTACHMENT_UPLOAD_TO = 'messaging/email/templates/attachments/'

STATICFILES_DIRS = (
    local_path('static/'),
)

STATICFILES_FINDERS = (
    'pipeline.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
    'pipeline.finders.CachedFileFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SECURE_URLS = True
AWS_PRELOAD_METADATA = True

# custom headers for files uploaded to amazon
expires = datetime.utcnow() + timedelta(days=(25 * 365))
expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
AWS_HEADERS = {
    'Cache-Control': 'max-age=1314000',
    'Expires': expires,
}

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_YUI_BINARY = 'yuicompressor'

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.closure.ClosureCompressor'
PIPELINE_CLOSURE_BINARY = 'closure'
PIPELINE_CLOSURE_ARGUMENTS = '--language_in ECMASCRIPT5'

PIPELINE_DISABLE_WRAPPER = True

COLLECTFAST_CACHE = 'collectfast'

try:
    from lily.pipeline.bundles import *
except ImportError:
    raise Exception("Missing pipeline bundles: define your static bundles in pipeline/bundles.py")

#######################################################################################################################
# LOGIN SETTINGS                                                                                                      #
#######################################################################################################################
LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('dashboard')
LOGOUT_URL = reverse_lazy('logout')
PASSWORD_RESET_TIMEOUT_DAYS = os.environ.get('PASSWORD_RESET_TIMEOUT_DAYS', 7)  # Also used as timeout for activation link
USER_INVITATION_TIMEOUT_DAYS = os.environ.get('USER_INVITATION_TIMEOUT_DAYS', 7)
CUSTOM_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = (
    'lily.users.auth_backends.EmailAuthenticationBackend',
)

#######################################################################################################################
# MIDDLEWARE CLASSES                                                                                                  #
#######################################################################################################################
MIDDLEWARE_CLASSES = (
    # See https://docs.djangoproject.com/en/dev/ref/middleware/#middleware-ordering for ordering hints
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'newrelicextensions.middleware.NewRelicMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'lily.tenant.middleware.TenantMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # 'lily.utils.middleware.PrettifyMiddleware', # Nice for debugging html source, but places whitespace in textareas
    )

#######################################################################################################################
# TEMPLATE SETTINGS                                                                                                   #
#######################################################################################################################
# Template settings
TEMPLATE_DIRS = (
    local_path('templates/')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    # 'django.core.context_processors.i18n',
    # 'django.core.context_processors.media',
    'django.core.context_processors.request',
    # 'django.core.context_processors.static',
    # 'django.core.context_processors.tz',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'lily.messaging.email.context_processors.email',
    'lily.utils.context_processors.quickbutton_forms',
    'lily.utils.context_processors.current_site',
)

# Disable caching in a development environment
if DEBUG:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
else:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )

#######################################################################################################################
# INSTALLED APPS                                                                                                      #
#######################################################################################################################
INSTALLED_APPS = (
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.formtools',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    # 3rd party
    'activelink',
    'bootstrap3',
    'django_extensions',
    'djangoformsetjs',
    'easy_thumbnails',
    'gunicorn',
    'pipeline',
    'collectfast',
    'templated_email',
    'storages',
    'south',
    'taskmonitor',
    'injector',
    'elasticutils',

    # Lily
    'lily',  # required for management command
    'lily.accounts',
    'lily.activities',
    'lily.cases',
    'lily.deals',
    'lily.contacts',
    'lily.messaging',
    'lily.notes',
    'lily.provide',
    'lily.search',
    'lily.tags',
    'lily.tenant',
    'lily.updates',
    'lily.users',
    'lily.utils',
    'lily.parcels',
    'lily.socialmedia',
)

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
        'template_debug',  # in-template tags for debugging purposes
    )

MESSAGE_APPS = (
    'lily.messaging.email',
)
INSTALLED_APPS += MESSAGE_APPS

#######################################################################################################################
# EMAIL SETTINGS                                                                                                      #
#######################################################################################################################
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_USE_TLS = boolean(os.environ.get('EMAIL_USE_TLS', 0))
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.host.com')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-username')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-password')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'example@provider.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'example@provider.com')
EMAIL_CONFIRM_TIMEOUT_DAYS = os.environ.get('EMAIL_CONFIRM_TIMEOUT_DAYS', 7)

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
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'extended': {
            'format': '[%(asctime)s] %(filename)s#%(lineno)s %(funcName)s(): %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'extended'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'search': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

if DEBUG:
    LOGGING['handlers']['console'].update({
        'filters': [],
    })
    LOGGING['loggers'].update({
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    })

#######################################################################################################################
# CACHING CONFIG                                                                                                      #
#######################################################################################################################
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
            'TIMEOUT': 60,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }
else:
    redis_url = urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost:6379'))
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
            'TIMEOUT': 300,  # Default django value of 5 minutes
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': redis_url.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
        'staticfiles': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
            'TIMEOUT': 31536000,  # One year, from django 1.7 this can be set to None for keys to never expire
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': redis_url.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
        'collectfast': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
            'TIMEOUT': 900,  # 15 minutes should be enough for upload to amazon
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': redis_url.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
    }

#######################################################################################################################
# NEW RELIC SETTINGS                                                                                                  #
#######################################################################################################################
NEW_RELIC_EXTENSIONS_ENABLED = boolean(os.environ.get('NEW_RELIC_EXTENSIONS_ENABLED', 0))
NEW_RELIC_EXTENSIONS_DEBUG = boolean(os.environ.get('NEW_RELIC_EXTENSIONS_DEBUG', 1))
NEW_RELIC_EXTENSIONS_ATTRIBUTES = {
    'user': {
        'username': 'Django username',
        'is_superuser': 'Django super user',
        'is_staff': 'Django staff user',
    },
    'is_secure': 'Secure connection',
    'is_ajax': 'Ajax request',
    'method': 'Http Method',
    'COOKIES': 'Http cookies',
    'META': 'Http meta data',
    'session': 'Http session',
}

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

ES_URLS = [es_url_to_dict(os.environ.get('SEARCHBOX_SSL_URL', 'http://localhost:9200'))]

# The indexes Elasticsearch uses.
ES_INDEXES = {'default': 'main_index'}

# Enable models for search. Used for batch indexing and realtime updating.
ES_MODEL_MAPPINGS = (
    'lily.accounts.search.AccountMapping',
    'lily.contacts.search.ContactMapping',
)

#######################################################################################################################
# MISCELLANEOUS SETTINGS                                                                                              #
#######################################################################################################################
# Registration form
REGISTRATION_POSSIBLE = boolean(os.environ.get('REGISTRATION_POSSIBLE', 0))

# Messaging framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# Tenant support
MULTI_TENANT = boolean(os.environ.get('MULTI_TENANT', 0))

# Settings for 3rd party apps

# django debug toolbar
INTERNAL_IPS = (['127.0.0.1'] + (['192.168.%d.%d' % (i, j) for i in [0, 1, 23] for j in range(256)])) if DEBUG else []

# dataprovider
DATAPROVIDER_API_KEY = os.environ.get('DATAPROVIDER_API_KEY')

# easy-thumbnails
THUMBNAIL_DEBUG = boolean(os.environ.get('THUMBNAIL_DEBUG', 0))
THUMBNAIL_QUALITY = os.environ.get('THUMBNAIL_QUALITY', 85)

# django-south
SOUTH_AUTO_FREEZE_APP = True
SOUTH_VERBOSITY = 1

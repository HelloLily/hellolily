import os
from urlparse import urlparse, uses_netloc

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import gettext_noop
from datetime import datetime, timedelta
import django.conf.global_settings as DEFAULT_SETTINGS


# Register database scheme and redis caching in URLs
uses_netloc.append('postgres')
uses_netloc.append('redis')

# Turn 0 or 1 into False or True
boolean = lambda value: bool(int(value))

# Get local path for any given folder/path
local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

# Try to read as much configuration from ENV
DEBUG = boolean(os.environ.get('DEBUG', 0))
DEV = boolean(os.environ.get('DEV', 0))
TEMPLATE_DEBUG = DEBUG

ADMINS = eval(os.environ.get('ADMINS', '()'))
MANAGERS = ADMINS

if DEV: # Only use sqlite db when in dev mode, Heroku injects db settings on deployment
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'local.sqlite',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
else:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default='postgres://localhost')
    }

SITE_ID = os.environ.get('SITE_ID', 1)

# Localization
TIME_ZONE = 'Europe/Amsterdam'
DATE_INPUT_FORMATS = tuple(['%d/%m/%Y'] + list(DEFAULT_SETTINGS.DATE_INPUT_FORMATS))
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('nl', gettext_noop('Dutch')),
    ('en', gettext_noop('English')),
)
USE_I18N = boolean(os.environ.get('USE_I18N', 1))
USE_L10N = boolean(os.environ.get('USE_L10N', 1))
USE_TZ = boolean(os.environ.get('USE_TZ', 1))
FIRST_DAY_OF_WEEK = os.environ.get('FIRST_DAY_OF_WEEK', 1)

# Don't share this with anybody
SECRET_KEY = os.environ.get('SECRET_KEY', 'my-secret-key')

# Security parameters
CSRF_COOKIE_SECURE = boolean(os.environ.get('CSRF_COOKIE_SECURE', 0)) # For production this needs to be set to True
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
SESSION_COOKIE_SECURE = boolean(os.environ.get('SESSION_COOKIE_SECURE', 0)) # For production this needs to be set to True
SESSION_COOKIE_HTTPONLY = boolean(os.environ.get('SESSION_COOKIE_HTTPONLY', 0)) # For production this needs to be set to True
SESSION_EXPIRE_AT_BROWSER_CLOSE = boolean(os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', 0))
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'SAMEORIGIN') # For production this needs to be set to DENY

# Media and static file locations

# Media
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', local_path('files/media/'))
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

ACCOUNT_UPLOAD_TO = 'images/profile/account'
CONTACT_UPLOAD_TO = 'images/profile/contact'

# Static
STATIC_ROOT = os.environ.get('STATIC_ROOT', local_path('files/static/'))
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

STATICFILES_DIRS = (
    local_path('static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Login settings
LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('dashboard')
LOGOUT_URL = reverse_lazy('logout')
PASSWORD_RESET_TIMEOUT_DAYS = os.environ.get('PASSWORD_RESET_TIMEOUT_DAYS', 7) # Also used as timeout for activation link
USER_INVITATION_TIMEOUT_DAYS = os.environ.get('USER_INVITATION_TIMEOUT_DAYS', 7)
CUSTOM_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = (
    'lily.users.auth_backends.EmailAuthenticationBackend',
)

# Used middleware
MIDDLEWARE_CLASSES = (
    # Mediagenerator (needs to be first)
    'mediagenerator.middleware.MediaMiddleware', # only used in dev mode
    
    # Django
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Third party
    'newrelicextensions.middleware.NewRelicMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    # Lily
    'lily.tenant.middleware.TenantMiddleWare',
#    'lily.utils.middleware.PrettifyMiddleware', # Nice for debugging html source, but places whitespace in textareas
)

# Main urls file
ROOT_URLCONF = 'lily.urls'

# WSGI setting
WSGI_APPLICATION = 'lily.wsgi.application'

# Template settings
TEMPLATE_DIRS = (
    local_path('templates/')
)

# overwriting defaults, to leave out media and static context processors
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'lily.utils.context_processors.quickbutton_forms',
)

# Disable caching in a development environment
if not DEBUG:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )
else:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

# Used and installed apps
INSTALLED_APPS = (
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    # 3rd party
    'templated_email',
    'easy_thumbnails',
    'gunicorn',
    'activelink',
    'south',
    'debug_toolbar',
    'mediagenerator',
    'storages',
    'crispy_forms',
#    'template_debug', in-template tags for debugging purposes

    # Lily
    'lily', # required for management command
    'lily.accounts',
    'lily.activities',
    'lily.cases',
    'lily.deals',
    'lily.contacts',
    'lily.notes',
    'lily.provide',
    'lily.tags',
    'lily.tenant',
    'lily.users',
    'lily.utils',
)

# E-mail settings
EMAIL_USE_TLS = boolean(os.environ.get('EMAIL_USE_TLS', 0))
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.host.com')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-username')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-password')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'example@provider.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'example@provider.com')
EMAIL_CONFIRM_TIMEOUT_DAYS = os.environ.get('EMAIL_CONFIRM_TIMEOUT_DAYS', 7)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level':'DEBUG',
            'filters': ['require_debug_false'],
            'class':'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
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
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}

# Messaging framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# Tenant support
TENANT_MIXIN = 'django.db.models.Model' # prevent models from breaking, use the default base model
if boolean(os.environ.get('MULTI_TENANT', 0)) and 'lily.tenant' in INSTALLED_APPS:
    TENANT_MIXIN = 'lily.tenant.models.TenantMixin'

# Settings for 3rd party apps

# django debug toolbar
INTERNAL_IPS = (['192.168.%d.%d' % (i, j) for i in [0, 1, 23] for j in range(256)]) if DEBUG else []
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# dataprovider
DATAPROVIDER_API_KEY = os.environ.get('DATAPROVIDER_API_KEY')

# easy-thumbnails
THUMBNAIL_DEBUG = boolean(os.environ.get('THUMBNAIL_DEBUG', 0))
THUMBNAIL_QUALITY = os.environ.get('THUMBNAIL_QUALITY', 85)

# django-templated-email
TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'

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

# django-redis-cache
if os.environ.get('REDISTOGO_URL', '') and boolean(os.environ.get('ENABLE_CACHE', 1)):
    url = urlparse(os.environ['REDISTOGO_URL'])
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': "{0.hostname}:{0.port}".format(url),
            'OPTIONS': {
                'PASSWORD': url.password,
                'DB': 0
            }
        }
    }

# django-mediagenerator
MEDIA_DEV_MODE = boolean(os.environ.get('MEDIA_DEV_MODE', DEBUG))
IGNORE_APP_MEDIA_DIRS = () # empty to include admin media
GENERATED_MEDIA_DIR = local_path('generated_media_dir/static')
GENERATED_MEDIA_DIRS = (local_path('generated_media_dir'),)

DEV_MEDIA_URL =  os.environ.get('DEV_MEDIA_URL', '/static/')
PRODUCTION_MEDIA_URL = os.environ.get('PRODUCTION_MEDIA_URL', DEV_MEDIA_URL)

YUICOMPRESSOR_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib', 'yuicompressor-2.4.7.jar')
ROOT_MEDIA_FILTERS = {
    'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
    'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
}

try:
    import mediagenerator
    MEDIA_BUNDLES = mediagenerator.MEDIA_BUNDLES
except ImportError:
    raise Exception("Missing MEDIA_BUNDLES: define your media_bundles in mediagenerator.py")

# django-storages
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') 
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') 
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# custom headers for files uploaded to amazon
expires = datetime.utcnow() + timedelta(days=(25 * 365))
expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
AWS_HEADERS = {
    'Cache-Control': 'max-age=1314000',
    'Expires': expires,
}

# cripsy-forms
CRISPY_TEMPLATE_PACK = 'mws-admin'
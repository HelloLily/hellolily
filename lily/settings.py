import os
from urlparse import urlparse, uses_netloc
from django.core.urlresolvers import reverse_lazy

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)
uses_netloc.append('postgres')
uses_netloc.append('redis')

DEBUG = os.environ.get('DEBUG', False)
DEV = os.environ.get('DEV', False)
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

if DEV: # Only use sqlite db when in dev mode, Heroku injects db settings on deployment
    DATABASES = { # Check: https://docs.djangoproject.com/en/dev/ref/settings/#databases
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'local.sqlite',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'NL-nl'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True
FIRST_DAY_OF_WEEK = 1

# Don't share this with anybody.
SECRET_KEY = os.environ.get('SECRET_KEY', 'my-secret-key')

CSRF_COOKIE_SECURE = False #For production this needs to be set to True
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

SESSION_COOKIE_SECURE = False #For production this needs to be set to True
SESSION_COOKIE_HTTPONLY = False #For production this needs to be set to True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
X_FRAME_OPTIONS = 'SAMEORIGIN' #For production this needs to be set to DENY

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', local_path('media/'))
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

STATIC_ROOT = os.environ.get('STATIC_ROOT', local_path('static_collected/'))
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

#LOGIN STUFF
LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('dashboard')
LOGOUT_URL = reverse_lazy('logout')
AUTHENTICATION_BACKENDS = (
    'lily.users.auth_backends.UserModelBackend',
)
PASSWORD_RESET_TIMEOUT_DAYS = 7 # Also used as timeout for activation link
USER_INVITATION_TIMEOUT_DAYS = 7
CUSTOM_USER_MODEL = 'users.UserModel'

STATICFILES_DIRS = (
    local_path('static/'),
    # Optional: see https://docs.djangoproject.com/en/1.3/ref/contrib/staticfiles/#prefixes-optional
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

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

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lily.urls'
WSGI_APPLICATION = 'lily.wsgi.application'

TEMPLATE_DIRS = (
    local_path('templates/')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

INSTALLED_APPS = (
    # Django
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    
    # 3rd party
    'templated_email',
    'gunicorn',
    
    # Lily
    'lily',
    'lily.accounts',
    'lily.activities',
    'lily.contacts',
    'lily.users',
    'lily.utils',
)

# Settings for templated e-mail app
TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'

DEFAULT_FROM_EMAIL = 'lily@hellolily.com'
SERVER_EMAIL = 'lily@hellolily.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'lily@hellolily.com'
EMAIL_HOST_PASSWORD = 'hellolily'
EMAIL_PORT = 587

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# TODO add the add-on on heroku first(!) and then enable this.

# Cache configuration
#if not DEBUG:
#    url = urlparse(os.environ['REDISTOGO_URL'])
#    CACHES = {
#        'default': {
#            'BACKEND': 'redis_cache.RedisCache',
#            'LOCATION': "{0.hostname}:{0.port}".format(url),
#            'OPTIONS': {
#                'PASSWORD': url.password,
#                'DB': 0
#            }
#        }
#    }



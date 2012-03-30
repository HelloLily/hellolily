from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
import os
import site_settings

DEBUG = TEMPLATE_DEBUG = False
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'En-en' # 'NL-nl'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True
FIRST_DAY_OF_WEEK = 1

CSRF_COOKIE_SECURE = True
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static_collected')
STATIC_URL = '/static/'

#LOGIN STUFF
LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = reverse_lazy('logout')
AUTHENTICATION_BACKENDS = (
    'lily.users.auth_backends.UserModelBackend',
)
PASSWORD_RESET_TIMEOUT_DAYS = 7 # Also used as timeout for activation link
USER_INVITATION_TIMEOUT_DAYS = 7
CUSTOM_USER_MODEL = 'users.UserModel'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
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
    os.path.join(PROJECT_ROOT, 'templates')
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
    
    # Lily
    'lily.accounts',
    'lily.activities',
    'lily.contacts',
    'lily.users',
    'lily.utils',
)

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

# Cache settings
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'TIMEOUT': 300
#    }
#}

# Settings for templated e-mail app
TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'

try:
    from site_settings import *
except:
    pass

if not hasattr(site_settings, 'DEFAULT_FROM_EMAIL'):
    raise ImproperlyConfigured('Missing DEFAULT_FROM_EMAIL in site_settings')

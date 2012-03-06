DEBUG = TEMPLATE_DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
DATABASES = { # Check: https://docs.djangoproject.com/en/dev/ref/settings/#databases
    'default': {
        'ENGINE': 'django.db.backends.example',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Custom email settings, only override if necessary
#DEFAULT_FROM_EMAIL = 'webmaster@localhost'
#SERVER_EMAIL = 'root@localhost'
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'youremail@gmail.com'
#EMAIL_HOST_PASSWORD = 'yourpassword'
#EMAIL_PORT = 587

# Don't share this with anybody!
# Generate a key here: http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = 'example'

CSRF_COOKIE_SECURE = False
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
X_FRAME_OPTIONS = 'ALLOW'
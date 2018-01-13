import dj_database_url
from .settings_base import *


DEBUG = False
COMPRESS_ENABLED = True

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL_PRODUCTION'))
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level':'DEBUG',
            # 'class':'logging.FileHandler',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_ROOT,
            'maxBytes': 1024 * 1024 * 20,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'logfile']
    },
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

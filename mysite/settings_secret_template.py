import os

DEBUG = True
INTERNAL_IPS = ['127.0.0.1']

SECRET_KEY = '2os^&jga#!bs86mb4*%0&9@2wdcz5qu=#u#=t+2nns2l3$m#ho'
# http://www.miniwebtool.com/django-secret-key-generator/

MIDDLEWARE_DEBUG = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

APPS_DEBUG = [
    'debug_toolbar'
]

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        'NAME': '',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': '',
        'PASSWORD': '',
    },
}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

CORS_ORIGIN_WHITELIST = (
)
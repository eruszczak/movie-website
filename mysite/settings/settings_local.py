import dj_database_url
from .settings_base import *


DEBUG = True
COMPRESS_ENABLED = False

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL_LOCAL'))
}

INSTALLED_APPS += [
    'debug_toolbar'
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

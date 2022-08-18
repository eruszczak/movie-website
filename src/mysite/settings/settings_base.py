import os
import json
# from celery.schedules import crontab
import dj_database_url

DEBUG = os.environ.get('DEBUG') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED') == 'True'
print(os.environ.items())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIR = os.path.dirname(BASE_DIR)
BACKUP_ROOT = os.path.join(PROJECT_DIR, 'backup')

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL', 'postgres://postgres:postgres@movie-database:5432/db'))
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'rest_framework',
    'corsheaders',
    'compressor',
    'widget_tweaks',

    'shared.apps.SharedConfig',
    'accounts.apps.AccountsConfig',
    'titles.apps.TitlesConfig',
    'lists.apps.ListsConfig',
    'importer.apps.ImporterConfig'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'mysite.urls'
WSGI_APPLICATION = 'mysite.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(PROJECT_DIR, 'media'))

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(PROJECT_DIR, 'static'))
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'home'
AUTH_USER_MODEL = 'accounts.User'

ADMINS = json.loads(os.environ.get('ADMINS', '[]'))
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = '[]'
EMAIL_SUBJECT_PREFIX = '[] '

ALLOWED_HOSTS = json.loads(os.environ.get('ALLOWED_HOSTS', '[]'))
CORS_ORIGIN_WHITELIST = json.loads(os.environ.get('CORS_ORIGIN_WHITELIST', '[]'))



CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'movie-website',
    }
}



# CELERY_BROKER_URL = 'redis://movie-redis:6379'
# CELERY_RESULT_BACKEND = 'redis://movie-redis:6379'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html?highlight=crontab%20#crontab-schedules
# CELERY_BEAT_SCHEDULE = {
#     # 'hello': {
#     #     'task': 'app.tasks.hello',
#     #     'schedule': crontab()  # execute every minute
#     # }
# }
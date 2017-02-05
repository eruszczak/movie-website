from .settings_secret import *


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

EXTERNAL_APPS = [
    'crispy_forms',
    'rest_framework',
    'corsheaders',
    'debug_toolbar',
]

LOCAL_APPS = [
    'movie',
    'recommend',
    'users',
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'mysite.urls'

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

WSGI_APPLICATION = 'mysite.wsgi.application'

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")

CRISPY_TEMPLATE_PACK = 'bootstrap3'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

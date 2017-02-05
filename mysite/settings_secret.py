import os

DEBUG = os.getenv('DJANGODEBUG', True)

SECRET_KEY = 'k2r@=*7hx$v!+pnk3v**x^j52p82!t_v%nr2kt!)o99d(98l_x'
# http://www.miniwebtool.com/django-secret-key-generator/

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        'NAME': 'site',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'PASSWORD': '123123aA',
    },
}
# http://stackoverflow.com/questions/1626326/how-to-manage-local-vs-production-settings-in-django/15315143#15315143
# DATABASES['default']['PASSWORD'] = 'f9kGH...'

GOOGLE_API_KEY = 'AIzaSyDtmWk9G0ChsRaU54SpGvWMoAePwua3gqY'

EMAIL_HOST = 'poczta.o2.pl'
EMAIL_HOST_USER = 'testpython@o2.pl'
EMAIL_HOST_PASSWORD = '123123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_DEST = 'kasumierka@gmail.com'


ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'kierrez.pythonanywhere.com', '193.70.36.10']

CORS_ORIGIN_WHITELIST = (
    'google.com',
    'kierrez.github.io',
)
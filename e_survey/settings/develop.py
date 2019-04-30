from .base import *

DEBUG = True

CORS_ORIGIN_ALLOW_ALL = True

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

## Configuración de la base de datos ##
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'PORT':     5432,
        'HOST':     '10.1.148.145',
        'NAME':     'e_survey',
        'USER':     'esurvey',
        'PASSWORD': 'abc$123456'
    }
}
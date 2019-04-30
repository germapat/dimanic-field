from .base import *

DEBUG = False

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"), 
)

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

## Configuraci�n de la base de datos ##

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'PORT':     5432,
        'HOST':     '10.1.1.252',
        'NAME':     'db_sysform',
        'USER':     'app_sysform',
        'PASSWORD': '4pP+_Sy1sf0rM*'
    }
}
from modcandy.settings.base import *

STATIC_URL = '/static/'
STATIC_ROOT = f"{BASE_DIR}/site/static/"
MEDIA_URL = '/media/'
MEDIA_ROOT = f'{BASE_DIR}/site/media/'

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('RDS_DB_NAME'),
            'USER': config('RDS_USERNAME'),
            'PASSWORD': config('RDS_PASSWORD'),
            'HOST': config('RDS_HOSTNAME'),
            'PORT': config('RDS_PORT'),
        }
    }
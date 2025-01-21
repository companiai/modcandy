from modcandy.settings.base import *

STATIC_URL = '/static/'
STATIC_ROOT = ''
MEDIA_URL = '/media/'
MEDIA_ROOT = f'{BASE_DIR}/site/media/'

STATICFILES_DIRS = (f'{BASE_DIR}/site/static/',)
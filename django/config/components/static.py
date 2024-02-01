import os.path
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

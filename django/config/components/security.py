import os

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

INTERNAL_IPS = [
    '127.0.0.1',
]
CSRF_TRUSTED_ORIGINS = ['http://0.0.0.0:8080', 'http://127.0.0.1:8080', 'http://localhost:8080']

CORS_ALLOWED_ORIGINS = ['http://0.0.0.0:8888',]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

import os

from .settings import *  # noqa: F403

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'test-secret-key')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5433'),
        'NAME': os.getenv('DB_NAME', 'prospect_tracker'),
        'USER': os.getenv('DB_USER', 'jhondel'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'jhondel'),
    }
}

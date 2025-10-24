import os
from .base import *

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['bt2-nine.vercel.app']
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
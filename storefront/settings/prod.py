import os
from .common import *

DEBUG = False

# https://djecrety.ir/ # heroku config:set SECRET_KEY='key value'
# SECRET_KEY = os.environ['SECRET_KEY']
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
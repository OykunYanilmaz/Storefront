import os
from .common import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']  # https://djecrety.ir/ # heroku config:set SECRET_KEY='key value'

ALLOWED_HOSTS = []  # heroku place

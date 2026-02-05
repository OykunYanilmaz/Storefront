import os
import dj_database_url
from .common import *

DEBUG = False

# https://djecrety.ir/ # heroku config:set SECRET_KEY='key value'
# SECRET_KEY = os.environ['SECRET_KEY']
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")


DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=False,
    )
}

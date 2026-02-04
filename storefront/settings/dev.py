from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-s*vq+2768$4_m_h5aspswh!3kdr0&p(^%@vlcgyi5)lt9#2$ad'

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'storefront2',
        'NAME': 'storefront3',
        'HOST': 'localhost',
        'USER': 'root',
        # 'PASSWORD': 'Mysql_84'
        'PASSWORD': 'P@ssword'
    }
}

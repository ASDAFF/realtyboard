# -*- coding: utf-8 -*-

# Django settings for realtyboard project.
from __future__ import absolute_import

import os.path
import sys
import logging
from datetime import timedelta


BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
RESULT_BACKEND = 'redis://localhost:6379/1'

CELERY_TIMEZONE = 'Europe/Kiev'

from datetime import timedelta

# CELERYBEAT_SCHEDULE = {
#     'add-every-30-seconds': {
#         'task': 'tasks.add',
#         'schedule': timedelta(seconds=30),
#         'args': (16, 16)
#     },
# }

CELERY_TIMEZONE = 'UTC'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)


#from kombu import serialization#
#serialization.registry._decoders.pop("application/x-python-serialize")
# CELERY_TASK_SERIALIZER = 'json',
# CELERY_RESULT_SERIALIZER = 'json',
# CELERY_ACCEPT_CONTENT = ['application/json']

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ('*', '127.0.0.1:8000')

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'noreply@ci.ua'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)



MANAGERS = ADMINS


#admin_tools
ADMIN_TOOLS_INDEX_DASHBOARD = 'realtyboard.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_MENU = 'realtyboard.menu.CustomMenu'

# GRAPPELLI
GRAPPELLI_ADMIN_TITLE = "CI.UA Admin"
GRAPPELLI_AUTOCOMPLETE_LIMIT = 9

AUTH_USER_MODEL = 'personal.UserData'
LOGIN_URL = '/accounts/login/'

LIQPAY_MERCHANT_ID = "i71110410506"
LIQPAY_SIGNATURE = "vW91gRW7dh40CBK9D4ZFKVQ0xDDwXIo5Uw0ZdjEg"

WEBMONEY_PURSE = "U163906996476"

DATABASES_MY = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'z:\\board_test',  # Or path to database file if using sqlite3.
        'USER': 'centrinform',  # Not used with sqlite3.
        'PASSWORD': 'tomtop',  # Not used with sqlite3.
        'HOST': '127.0.0.1',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.

    },
    'centrinform': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'centrinform',  # Or path to database file if using sqlite3.
        'USER': 'centrinform',  # Not used with sqlite3.
        'PASSWORD': 'tomtop',  # Not used with sqlite3.
        'HOST': '127.0.0.1',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ciua_board',  # Or path to database file if using sqlite3.
        'USER': 'ciua_ciua',  # Not used with sqlite3.
        'PASSWORD': 'ImM7XBCe',  # Not used with sqlite3.
        'HOST': 'localhost',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    },
    'centrinform': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ciua_centrinform',  # Or path to database file if using sqlite3.
        'USER': 'ciua_ciua',  # Not used with sqlite3.
        'PASSWORD': 'ImM7XBCe',  # Not used with sqlite3.
        'HOST': 'localhost',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    },
}

DATABASE_ROUTERS = ["importdb.dbroutes.ImportdbRouter"]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

SOUTH_MIGRATION_MODULES = {
    'pybb': 'pybb.south_migrations',
}

# Local time zone for this installation.  Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
# TIME_ZONE = 'Europe/Zaporozhye'
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation.  All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
CKEDITOR_UPLOAD_PATH = MEDIA_ROOT + "/ckeditor"
# URL that handles the media served from MEDIA_ROOT.  Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = '/data/python/estate-kharkov.ci.ua/realtyboard/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'realtyboard/static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(PROJECT_PATH, 'static/'),)
# BAZADIR = os.path.join(PROJECT_PATH, 'media/bazadocumets1233/')
# BAZADIR_KH = os.path.join(PROJECT_PATH, 'media/bazadocumets/')
# '/data/web/media'
BAZADIR = BAZADIR_KH = os.path.join(PROJECT_PATH, 'media/base_files/rar/')
#'/data/web/media/uploads/base_files/rar/'
# BASE_STORE = os.path.join(MEDIA_ROOT,'uploads', 'base_files', 'rar')

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n(bd1f1c%e8=_xad02x5qtfn%wgwpi492e$8_erx+d)!tpeoim'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pybb.middleware.PybbMiddleware',
    # 'realtyboard.crooss_auth.CroossAuth',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'realtyboard.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'realtyboard.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

# List of callables that know how to importdb templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.templates.loaders.eggs.Loader',
)
# FIX ME нужно с этим что-то делать ^-^
# print("PATH", os.path.join(PROJECT_PATH, 'templates'))
INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'board',
    'ckeditor',
    # 'grab',
    'gunicorn',
    # 'importdb',
    'lesnoe',
    'lukomorye',
    'news',
    'pagination',
    'personal',
    'qrcode',
    'slparser',
    'south',
    # 'vparser',
    'tour',
    'xlsxwriter',
    'xlrd',
    'pybb',
    'debug_toolbar',
#    'djcelery',
#    'djkombu',
#    'haystack',
#    'grappelli',
#    'accounts',
#    'djangotoolbox',
#    'djangosphinxsearch',
#   'djangosphinx',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "realtyboard.context_processors.city",
    'pybb.context_processors.processor',
)

CKEDITOR_CONFIGS = {
   'default': {
       'toolbar': 'full',
       'height': 300,
       'width': 'auto',
   },
   'foreword': {
      'toolbar': 'full',
       'height': 200,
       'width': 700,
   },
   'article': {
      'toolbar': 'full',
       'height': 400,
       'width': 700,
   },
}

PROXY_CREDENTIALS = {
    'fine': 'UA88061:BGVJmPKiOj',
    # 'elite': 'UA111496:WgN0eYlxA4',
}

# A sample logging configuration.  The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

USD_UAH = 26

try:
    from realtyboard.local_settings import *
except ImportError:
    pass

    

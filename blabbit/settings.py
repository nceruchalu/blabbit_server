"""
Django settings for blabbit project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import socket
import logging
from datetime import datetime, timedelta

# import sensitive information and be sure to have SECRET_KEY setup
from settings_secret import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# DEBUG mode will only happen on my local machine
if socket.gethostname() == 'Nnodukas-MacBook-Pro.local':
    DEBUG = True
else:
    DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Noddy', 'nceruchalu@gmail.com'),
    )
MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['www.blabb.it', 'blabb.it', 'nceruchalu.webfactional.com']


# ---------------------------------------------------------------------------- #
# Application definition
# ---------------------------------------------------------------------------- #

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'imagekit',
    'rest_framework',
    'haystack',
    'blabbit.apps.account',
    'blabbit.apps.relationship',
    'blabbit.apps.conversation',
    'blabbit.apps.explore',
    'blabbit.apps.search',
    'blabbit.apps.feedback',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'blabbit.urls'

WSGI_APPLICATION = 'blabbit.wsgi.application'


# ---------------------------------------------------------------------------- #
# Database
# ---------------------------------------------------------------------------- #
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': DATABASES_PSQL_NAME,
        'USER': DATABASES_PSQL_USER,
        'PASSWORD': DATABASES_PSQL_PASSWORD,
        'HOST': '',
        'PORT': '',
    }
}

# ---------------------------------------------------------------------------- #
# Internationalization
# ---------------------------------------------------------------------------- #
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# ---------------------------------------------------------------------------- 
# Static files (CSS, JavaScript, Images)
# ---------------------------------------------------------------------------- 
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
if DEBUG == True:
    STATIC_URL = '/static/'
else:
    STATIC_URL = AWS_STATIC_BUCKET_URL

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'static').replace('\\','/'),
    )


# ---------------------------------------------------------------------------- 
# Template files (HTML)
# ---------------------------------------------------------------------------- 
TEMPLATE_DIRS = (
        os.path.join(os.path.dirname(__file__), 'templates'),
        )


# ---------------------------------------------------------------------------- 
# Logging
# ---------------------------------------------------------------------------- 
# https://docs.djangoproject.com/en/1.6/topics/logging/

# This logging configuration does the following:
# - identifies the configuration as being in `dictConfig version 1` format. 
# - defines 2 formatters: simple and verbose
# - defines 2 handlers:
#   + console, a StreamHandler, which will print any DEBUG (or higher) message
#     to stderr. This handler uses the simple output format.
#   + mail_admins, an AdminEmailHandler, which will email any ERROR (or higher)
#     message to the site admins
# - configures 1 logger:
#   + django, which passes all messages at ERROR or higher to the mail_admins
#     handlers when not in DEBUG mode. In debug mode this logger passes messages
#     to the console handler.
#

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
            }
        },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
    }

if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']


# ---------------------------------------------------------------------------- #
# Amazon AWS storage settings
# ---------------------------------------------------------------------------- #
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Specify AWS S3 bucket to upload files to
if DEBUG == True:
    AWS_STORAGE_BUCKET_NAME = AWS_TEST_MEDIA_BUCKET_URL
else:
    AWS_STORAGE_BUCKET_NAME = AWS_MEDIA_BUCKET_URL

AWS_REDUCED_REDUNDANCY = True
expires=datetime.now() + timedelta(days=365)
AWS_HEADERS = {
    'Expires':expires.strftime('%a, %d %b %Y 20:00:00 GMT'),
}

# Read files from AWS cloudfront (requires using s3boto storage backend)
if DEBUG == True:
    AWS_S3_CUSTOM_DOMAIN = AWS_TEST_MEDIA_CLOUDFRONT_URL
else:
    AWS_S3_CUSTOM_DOMAIN = AWS_MEDIA_CLOUDFRONT_URL


# ---------------------------------------------------------------------------- #
# `account` settings
# ---------------------------------------------------------------------------- #
# specify custom user model
AUTH_USER_MODEL = 'account.User'
# max image file size: 25MB (applies to both accounts and rooms)
MAX_IMAGE_SIZE = 25 * 1024 * 1024


# ---------------------------------------------------------------------------- #
# `conversation` settings
# ---------------------------------------------------------------------------- #
# expiry time of rooms (in seconds)
ROOM_EXPIRY_TIME_SECONDS = 86400 # 24 hours


# ---------------------------------------------------------------------------- #
# ejabberd authentication settings
# ---------------------------------------------------------------------------- #
# use pythong logging levels:
# https://docs.python.org/2/library/logging.html#logging-levels
if DEBUG == True:
    EJABBERD_AUTH_LOG_LEVEL = logging.DEBUG
else:
    EJABBERD_AUTH_LOG_LEVEL = logging.ERROR

EJABBERD_AUTH_LOG = '/tmp/blabbit/ejabberd_auth.log'
    

# ---------------------------------------------------------------------------- #
# `imagekit` settings
# ---------------------------------------------------------------------------- #
# create appropriate thumbnails on source file save only
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY ='imagekit.cachefiles.strategies.Optimistic'
IMAGEKIT_CACHEFILE_DIR = 'cache'
IMAGEKIT_SPEC_CACHEFILE_NAMER ='imagekit.cachefiles.namers.source_name_as_path'


# ---------------------------------------------------------------------------- #
# Search engine (`haystack`) settings
# ---------------------------------------------------------------------------- #
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__),'whoosh/blabbit_index'),
        'INCLUDE_SPELLING': True, # include spelling suggestions
        },
}

# ---------------------------------------------------------------------------- #
# Email settings
# ---------------------------------------------------------------------------- #
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# rest of the settings are in settings_secret.py


# ---------------------------------------------------------------------------- #
# Django REST framework settings
# ---------------------------------------------------------------------------- #

REST_FRAMEWORK = {
    # Use an expiring token-based authentication scheme.
    'DEFAULT_AUTHENTICATION_CLASSES':(
        # token authentication is the default used by clients
        'blabbit.apps.account.authentication.ExpiringTokenAuthentication',
        # need session authentication for the Browseable API
        'rest_framework.authentication.SessionAuthentication',
        ),
    
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Allow authenticated users to perform any request,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
        ],
    
    # Use JSON format
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        ),
    
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
        ],
    
    'PAGINATE_BY': 100
}

# Uncomment to enable Browseable API in DEBUG mode only
#if DEBUG:
#    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += [
#        'rest_framework.renderers.BrowsableAPIRenderer'
#        ]

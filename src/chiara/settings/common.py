"""
Common Django settings for chiara project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
from chiara.settings.local import SRC_DIR, SERVER_ADRESS

# location of different directories
WEBDAV_DIR = os.path.join(SRC_DIR, 'webdav')
REPOSITORY_DIR = os.path.join(SRC_DIR, 'repository')
BASH_DIR = os.path.join(SRC_DIR, 'bash')

# name of system directories and files
COLLECTION_INFO_DIR ='_chiara'
COLLECTION_DESCRIPTION_FILE = 'description.txt'
COLLECTION_TRAITS_FILE = 'traits'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-#1skj4pqxma2-=gl*#uz5jw2nir7u=jv4c(nit79txww9(gel'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'authentication.User'

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'south',
    'djcelery',
    'djkombu',
    'omnibus',
    
    'progress',
    'authentication',
    'collection',
    'log',
    'lib',
)

# Template path
TEMPLATE_DIRS = (
    os.path.join(SRC_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authentication.models.CurrentUserMiddleware',
)

ROOT_URLCONF = 'chiara.urls'

WSGI_APPLICATION = 'chiara.wsgi.application'


# Celery
BROKER_URL = 'django://'
CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
#CELERY_IMPORTS = ('collection.models', )


# Websocket
OMNIBUS_ENDPOINT_SCHEME = 'ws'
OMNIBUS_SERVER_HOST = SERVER_ADRESS
OMNIBUS_SERVER_PORT = '4242'
OMNIBUS_WEBAPP_FACTORY = 'omnibus.factories.websocket_webapp_factory'
OMNIBUS_CONNECTION_FACTORY = 'omnibus.factories.websocket_connection_factory'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_L10N = True
USE_TZ = True

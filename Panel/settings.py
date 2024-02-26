"""
Django settings for Panel project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from django.conf import settings
from pathlib import Path
#
# from dotenv import load_dotenv
# load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
# PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
# print("****************")
# print(PAYPAL_CLIENT_ID)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Global_Core.settings')
settings.configure()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+m)(kslzi*om(rg!nm&%syw_n(p-dua2-90!sf_wpevjinunz+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
AUTH_USER_MODEL = 'Global_Core.CustomUser'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'paypal.standard.ipn'
    'Global_Core.apps.GlobalCoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Panel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]


WSGI_APPLICATION = 'Panel.wsgi.application'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
PAYPAL_TEST = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTHNET_DEBUG = True
AUTHORIZE_NET_LOGIN_ID = '57njF7yrLVFs'
AUTHORIZE_NET_TRANSACTION_KEY = '7z8bY25LdJs7R4Dj'
AUTHORIZENET_ENVIRONMENT = 'sandbox'


SQUARE_ACCESS_TOKEN = 'EAAAl2z8nouxfGLBcID8kiQYdBwJ4sU54S5UREZhqRuwMvvPg7MjOHHMTkSLMpU-'
SQUARE_LOCATION_ID = 'L2A4P9RWBX8J2'
SQUARE_APPLICATION_ID = 'sandbox-sq0idb-YGTPzC7WtzIuYTgHzFtSDg'




"""
Django settings for sea project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a^1#l#&@h^1%_8iing(x#xv7m7^jv*%x9q-b9jyprc9b&jjnyn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sea_app',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sea_app.middleware.ResponseMiddleware'
]

ROOT_URLCONF = 'sea.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'sea.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME':'sea',
    'USER': 'sea',
    'PASSWORD': 'sea@orderplus.com',
    'HOST': '47.112.113.252',
    # 'HOST': '127.0.0.1',
    'PORT': '3306',
    'OPTIONS': {"init_command": "SET foreign_key_checks = 0;",}
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

USE_TZ = False

AUTH_USER_MODEL = "sea_app.User"

APPEND_SLASH = False

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.BasicAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#         # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
#     )
# }

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_SECRET_KEY': 'sea',
}

shopify = {

}

pinterest = {

}

#######################
# DEFINE EMAIL CONFIG #
#######################

EMAIL_HOST = "smtpout.secureserver.net"
EMAIL_PORT = 465
EMAIL_HOST_USER = "service@pinbooster.seamarketings.com"
EMAIL_HOST_PASSWORD = "orderplus"
DEFAULT_FROM_EMAIL = "PinBooster Customer Support <service@pinbooster.seamarketings.com>"
EMAIL_USE_SSL = True
EMAIL_SUBJECT_PREFIX = " "
# 默认邮件接收方(开发人员，如果代码出现极端异常可进行邮件通知.)
DEFAULT_TO_EMAILS = ["877252373@qq.com", ]


# view 缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', #缓存到本地内存中
        'TIMEOUT': 60,
    }
}

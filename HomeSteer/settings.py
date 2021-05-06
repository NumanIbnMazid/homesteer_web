
import os
from decouple import config, Csv
from unipath import Path
# from dj_database_url import parse as db_url

BASE_DIR = Path(__file__).parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

EMAIL_BACKEND = config('EMAIL_BACKEND', default='')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third Party Apps
    'sslserver',
    'widget_tweaks',
    'django_cleanup',
    'django_cool_paginator',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    # Local Apps
    'accounts',
    'memberships',
    'rooms',
    'search',
    'tracker',
    'suspicious',
    'utils'
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    # 'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_PROVIDERS =  { 'facebook':
                               {'METHOD': 'oauth2',
                                'SCOPE': ['email', 'public_profile', 'user_friends'],
                                'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
                                'INIT_PARAMS': {'cookie': True},
                                'FIELDS': [
                                    'id',
                                    'email',
                                    'name',
                                    'first_name',
                                    'last_name',
                                    'verified',
                                    'locale',
                                    'timezone',
                                    'link',
                                    'gender',
                                    'updated_time',
                                ],
                                'EXCHANGE_TOKEN': True,
                                'LOCALE_FUNC': lambda request: 'en_US',
                                'VERIFIED_EMAIL': True,
                                'VERSION': 'v2.4'
                               }
                           }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HomeSteer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'HomeSteer.wsgi.application'


# DATABASES = {
#     'default': config(
#         'DATABASE_URL',
#         default='sqlite:///' + BASE_DIR.child('db.sqlite3'),
#         cast=db_url
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET storage_engine=InnoDB; \
                            SET sql_mode='STRICT_TRANS_TABLES'",
            'autocommit': True,
        },
        # 'OPTIONS': {
        #     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        # },
        # 'OPTIONS': {
        #     'init_command': 'ALTER DATABASE <config('DB_NAME')> CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci',
        # },
    }
}

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

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_L10N = True
# USE_TZ = True

LANGUAGE_CODE   = 'en-us'
TIME_ZONE       = 'Asia/Dhaka'
USE_I18N        = True
USE_L10N        = True
USE_TZ          = False


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_proj'),
]
STATIC_ROOT = os.path.join('static_cdn', 'static_root')
MEDIA_ROOT = os.path.join('static_cdn', 'media_root')


# ------------- Authentication Modules -------------
LOGIN_URL = config('LOGIN_URL', default='/account/login/')
LOGOUT_URL = config('LOGOUT_URL', default='/')
LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL', default='/')
SITE_NAME = config('SITE_NAME', default='HomeSteer')
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = config('ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS', default=7, cast=int)
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = config('ACCOUNT_LOGIN_ATTEMPTS_LIMIT', default=7, cast=int)
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = config('ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT', default=223, cast=int)
ACCOUNT_USERNAME_MIN_LENGTH = config('ACCOUNT_USERNAME_MIN_LENGTH', default=0, cast=int)
ACCOUNT_EMAIL_REQUIRED = config('ACCOUNT_EMAIL_REQUIRED', default=False, cast=bool)
ACCOUNT_USERNAME_REQUIRED = config('ACCOUNT_USERNAME_REQUIRED', default=False, cast=bool)
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = config('ACCOUNT_SIGNUP_PASSWORD_VERIFICATION', default=False, cast=bool)
ACCOUNT_UNIQUE_EMAIL = config('ACCOUNT_UNIQUE_EMAIL', default=False, cast=bool)
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = config('ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE', default=False, cast=bool)
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = config('ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE', default=False, cast=bool)
SOCIALACCOUNT_QUERY_EMAIL=config('SOCIALACCOUNT_QUERY_EMAIL', default=True, cast=bool)
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = config('ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL', default='/')
ACCOUNT_AUTHENTICATION_METHOD = config('ACCOUNT_AUTHENTICATION_METHOD', default='username')
ACCOUNT_EMAIL_VERIFICATION = config('ACCOUNT_EMAIL_VERIFICATION', default='mandatory')
ACCOUNT_EMAIL_SUBJECT_PREFIX = config('ACCOUNT_EMAIL_SUBJECT_PREFIX', default='HomeSteer')
ACCOUNT_USERNAME_BLACKLIST =['robot', 'hacker', 'virus', 'spam']
ACCOUNT_ADAPTER = 'HomeSteer.adapter.UsernameMaxAdapter'

# Cool Paginator Settings
COOL_PAGINATOR_NEXT_NAME        = "next"
COOL_PAGINATOR_PREVIOUS_NAME    = "previous"
COOL_PAGINATOR_SIZE             = "SMALL"
COOL_PAGINATOR_ELASTIC          = "300px"

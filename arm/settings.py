"""

AON 2023

"""
# CSRF_COOKIE_DOMAIN = '.192.168.0.102'

# Для корректной работы с Nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEBUG = True

# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

NV_REPORTS = dict(dbAlias='REPORTS', domain='rf_nv')

TEMPLATE_DIR = BASE_DIR / 'templates'

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticRoot'

MEDIA_ROOT = BASE_DIR / 'static' / 'media'
MEDIA_URL = "/media/"

API_DIR = BASE_DIR / 'arm' / 'api'
IMAGE_DIR = API_DIR / 'react' / 'images'
REPORT_DIR = BASE_DIR / 'nv_reports' / NV_REPORTS['domain']

LOG_DIR = BASE_DIR / 'log'
DB_DIR = BASE_DIR / 'DB'


# *** *** *** loadIniFile

import os

fromIni = {}

with open(os.path.join(BASE_DIR, 'DB', 'sova.ini'), 'rt') as f:
    for s in f.readlines():
        l, _, r = s.partition('=')
        l, r = l.strip(), r.strip()
        if r and not l.startswith('#'):
            fromIni[l] = r

SECRET_KEY = fromIni.get('SECRET_KEY')

# *** *** ***

SESSION_COOKIE_AGE = 3600 * 24 * 300

CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True



# *** *** ***

if 0 and DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
            },
        },
        'root': {
            'handlers': ['console'],
        }
    }

# *** *** ***

LOGIN_URL = '/api/login/'
LOGOUT_URL = '/admin/logout'
LOGIN_REDIRECT_URL = '/api/new?form=arm'
LOGOUT_REDIRECT_URL = '/'

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 15  # 15M
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

CSRF_TRUSTED_ORIGINS = []

# *** *** ***

ALLOWED_HOSTS = ['sova.online', 'result-systems.ru', '127.0.0.1', 'localhost', '192.168.0.102']
DEVELOPMENT_MODE = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.vk',
    'allauth.socialaccount.providers.yandex',

    'nv',
    'nv_c',
    'nv_lm',
    'nv_reports',
    'landing',
]

# состав extra_data определяется в вк-AllAuth в массиве USER_FIELDS
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email', ],
        'AUTH_PARAMS': {'access_type': 'online', }
    },
    'vk': {
        'SCOPE': ['friends', 'groups', 'email'],  # это права доступа
        'AUTH_PARAMS': {'access_type': 'online', }
    },
    'yandex': {
        'SCOPE': [],
        'AUTH_PARAMS': {'access_type': 'online', }
    }
}

QUERY_EMAIL = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.go1.unisender.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '5961271'
EMAIL_HOST_PASSWORD = '6zfwttxcbemtf969x7wpkaoku38qr8bad8x5tq8a'

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/email/confirm/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/accounts/email/confirm/'
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
# ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 3600
# ACCOUNT_RATE_LIMITS = ???????????????

DEFAULT_FROM_EMAIL = 'info@sova.online'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'arm.middleware.MobileMW',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'arm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'arm.wsgi.application'

DATABASE_ROUTERS = ['arm.multirouter.MultiRouter']

DATABASES = {
    'nv': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'DB/nv.sqlite3',
    },
    'lm': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'DB/lm.sqlite3',
    },
    'reports': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'DB/reports.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'DB/common.sqlite3',
    },
}

AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


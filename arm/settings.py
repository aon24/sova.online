"""

AON 2023

"""
from arm.tools.DC import config
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# *** *** *** loadIniFile
try:
    f = open('/etc/sova.ini')
except:
    f = open(os.path.join(BASE_DIR, 'DB', 'sova.ini'))

for s in f.readlines():
    l, _, r = s.partition('=')
    l, r = l.strip(), r.strip()
    if r and not l.startswith('#'):
        config[l] = r

f.close()

# ***

try:
    with open(os.path.join(BASE_DIR, 'DB', 'contacts.txt')) as f:
        config.contacts = f.read()
except:
    pass

LOG_DIR = config.LOG_DIR or BASE_DIR / 'log'
DB_DIR = config.DB_DIR or BASE_DIR / 'DB'

DEMO_MODE = config.DEMO_MODE
DEVELOPMENT_MODE = config.DEVELOPMENT_MODE

SECRET_KEY = config.SECRET_KEY
DEBUG = bool(config.DEBUG)
ALLOWED_HOSTS = [config.HOST]
ALLOWED_HOSTS += [h.strip() for h in config.addAllowedHosts.split(',')]

DEFAULT_FROM_EMAIL = config.DEFAULT_FROM_EMAIL
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = int(config.EMAIL_PORT or '587', 10)
EMAIL_USE_TLS = bool(config.EMAIL_USE_TLS)
EMAIL_HOST_USER = config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
if DEVELOPMENT_MODE:  # Письма сохраняются в файлы
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR / 'test_emails'
else:
    EMAIL_BACKEND = 'arm.tools.safeSmtp.SafeSMTPEmailBackend'

# *** *** ***
# Для корректной работы с Nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_COOKIE_SAMESITE = 'Lax'  # 'None'
CSRF_COOKIE_SECURE = True

# *** *** ***

SESSION_COOKIE_AGE = 3600 * 24 * 300
ACCOUNT_SESSION_REMEMBER = True

# *** *** ***

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
STATICFILES_DIRS = [STATIC_DIR]
MEDIA_ROOT = BASE_DIR / 'static' / 'media'

API_DIR = BASE_DIR / 'arm' / 'api'
REPORT_DIR = BASE_DIR / 'nv_reports' / 'rf_nv'

# *** *** ***

LOGIN_URL = '/api/login'
LOGIN_INVALID_URL = '/api/login?error=1'
LOGOUT_URL = '/admin/logout'
LOGIN_REDIRECT_URL = '/api/new?form=arm'
LOGOUT_REDIRECT_URL = '/'

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 15  # 15M
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

# *** *** ***


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
    'allauth.socialaccount.providers.yandex',

    'nv',
    'nv_c',
    'nv_lm',
    'nv_reports',
]

# состав extra_data определяется в вк-AllAuth в массиве USER_FIELDS
SOCIALACCOUNT_PROVIDERS = {
    'yandex': {
        'SCOPE': [],
        'AUTH_PARAMS': {'access_type': 'online', }
    }
}

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
    'django.contrib.messages.middleware.MessageMiddleware',  # без нее не работает админка
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # защиты от атак типа Clickjacking (подмена кликов)
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
        'NAME': DB_DIR / 'nv.sqlite3',
    },
    'lm': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_DIR / 'lm.sqlite3',
    },
    'reports': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_DIR / 'reports.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_DIR / 'common.sqlite3',
    },
}

AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {
        'min_length': 5,
    }
}]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


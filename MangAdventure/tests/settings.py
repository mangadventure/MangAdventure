"""The project's test settings."""

import re
from importlib.util import find_spec
from os import environ as env
from pathlib import Path
from secrets import token_urlsafe

from MangAdventure import __version__ as VERSION
from MangAdventure.bad_bots import BOTS

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = env.get('SECRET_KEY', token_urlsafe(37))

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost', '[::1]']

DEBUG = env.get('MANGADV_DEBUG', False)

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.reddit',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.discord',
    'rest_framework',
    'config',
    'reader',
    'api',
    'groups',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'MangAdventure.middleware.BaseMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'MangAdventure.middleware.PreloadMiddleware',
]

ROOT_URLCONF = 'MangAdventure.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'config.context_processors.extra_settings',
    ]},
    'DIRS': [BASE_DIR / 'MangAdventure' / 'templates'],
    'APP_DIRS': True
}]

WSGI_APPLICATION = 'MangAdventure.wsgi.application'

DATABASES = {'default': {
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'PASSWORD': env.get('DB_PASSWORD'),
        'NAME': 'mangadv',
        'USER': 'root',
        'HOST': '127.0.0.1',
        'PORT': 3306
    },
    'postgresql': {
        'ENGINE': 'django.db.backends.postgresql',
        'PASSWORD': env.get('DB_PASSWORD'),
        'NAME': 'mangadv',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': 5432
    }
}.get(env.get('DB_TYPE', 'sqlite3'))}

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    ('styles', str(STATIC_ROOT / 'styles')),
    ('scripts', str(STATIC_ROOT / 'scripts')),
    ('COMPILED', str(STATIC_ROOT / 'COMPILED')),
    ('extra', str(STATIC_ROOT / 'extra')),
    ('vendor', str(STATIC_ROOT / 'vendor')),
]

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'tests' / 'media'

USE_I18N = False

USE_L10N = True

USE_TZ = True

LANGUAGE_CODE = 'en-us'

LANGUAGE_COOKIE_NAME = 'mangadv_lang'

LANGUAGE_COOKIE_HTTPONLY = True

LANGUAGE_COOKIE_SAMESITE = 'Strict'

LANGUAGES = [
    ('en', 'English'),
]

TIME_ZONE = 'UTC'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'django.contrib.auth.password_validation.{n}Validator'}
    for n in ('UserAttributeSimilarity', 'MinimumLength',
              'CommonPassword', 'NumericPassword')
]

AUTHENTICATION_BACKENDS = [
    'users.backends.ScanlationBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'

ACCOUNT_USER_DISPLAY = 'users.get_user_display'

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

SOCIALACCOUNT_ADAPTER = 'users.adapters.SocialAccountAdapter'

SOCIALACCOUNT_EMAIL_REQUIRED = False

SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    'reddit': {
        'AUTH_PARAMS': {'duration': 'permanent'},
        'USER_AGENT': (
            f'Django:MangAdventure:{VERSION} '
            '(by https://github.com/mangadventure)'
        )
    },
    'discord': {
        'SCOPE': ['identify', 'email'],
    }
}

LOGIN_URL = '/user/login'

SESSION_COOKIE_AGE = 2592000

SESSION_COOKIE_HTTPONLY = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = 'evangelos-ch@users.noreply.github.com'

DISALLOWED_USER_AGENTS = [re.compile(re.escape(b), re.I) for b in BOTS]
DISALLOWED_USER_AGENTS.append(re.compile('^$'))  # empty UA

CSRF_COOKIE_HTTP_ONLY = True

CSRF_COOKIE_SAMESITE = 'Strict'

SESSION_COOKIE_SAMESITE = 'Strict'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = 'strict-origin'

LANGUAGE_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

env.setdefault('wsgi.url_scheme', 'https')

# XXX: No SSL on localhost
SECURE_SSL_REDIRECT = env.get('HTTPS', False)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.v2.pagination.PageLimitPagination',
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_SCHEMA_CLASS': 'api.v2.schema.OpenAPISchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.v2.auth.ApiKeyAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'api.v2.auth.ScanlatorPermissions',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DATETIME_INPUT_FORMATS': ('iso-8601', '%m/%d/%y'),
    'DEFAULT_THROTTLE_RATES': {'anon': '100/m'},
    'SCHEMA_COERCE_METHOD_NAMES': {
        'list': '* list',
        'create': '* create',
        'retrieve': '* read',
        'update': '* update',
        'partial_update': '* patch',
        'destroy': '* delete'
    },
    'URL_FORMAT_OVERRIDE': None,
    'ORDERING_PARAM': 'sort',
    'DEFAULT_VERSION': 'v2',
    'VERSION_PARAM': None,
    'SEARCH_PARAM': 'q',
}

if find_spec('csp'):
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')
    CSP_DEFAULT_SRC = ("'none'",)
    CSP_CONNECT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'",)
    CSP_STYLE_SRC = (
        "'self'", "https://fonts.googleapis.com", "https://cdn.statically.io"
    )
    CSP_FONT_SRC = (
        "'self'", "https://fonts.gstatic.com", "https://cdn.statically.io"
    )
    CSP_IMG_SRC = ("'self'", "https://cdn.statically.io")
    CSP_FORM_ACTION = ("'self'",)
    CSP_FRAME_SRC = ("'self'",)
    CSP_FRAME_ANCESTORS = ("'self'",)
    CSP_BASE_URI = ("'none'",)
    CSP_EXCLUDE_URL_PREFIXES = (
        '/api', '/admin-panel', '/robots.txt',
        '/opensearch.xml', '/contribute.json',
    )

CONFIG = {
    'NAME': 'MangAdventure',
    'DOMAIN': 'example.com',
    'DESCRIPTION': '',
    'KEYWORDS': 'mangadventure,manga,scanlation,reader',
    'DISCORD': '',
    'TWITTER': '',
    'FAVICON': '',
    'LOGO': '',
    'LOGO_TW': '',
    'LOGO_OG': '',
    'MAIN_BG_COLOR': '#FFF',
    'MAIN_TEXT_COLOR': '#000',
    'ALTER_BG_COLOR': '#AAA',
    'ALTER_TEXT_COLOR': '#555',
    'SHADOW_COLOR': '#444',
    'FONT_NAME': 'Lato',
    'FONT_URL': 'https://fonts.googleapis.com/css?family=Lato&display=swap',
    'USE_CDN': True,
    'ALLOW_DLS': True,
    'MAX_RELEASES': 10,
    'MAX_CHAPTERS': 1,
    'SHOW_CREDITS': True,
    'ENABLE_API_V1': True
}

del BOTS, VERSION

"""The project's settings."""

# NOTE: When this file is modified,
# MangAdventure/tests/settings.py
# should also be modified accordingly.

import re
from importlib.util import find_spec
from pathlib import Path

from yaenv import Env

from MangAdventure import __version__ as VERSION
from MangAdventure.bad_bots import BOTS

#: Build paths inside the project like this: ``BASE_DIR / ...``.
BASE_DIR = Path(__file__).resolve().parents[1]

# Load environment variables from .env file.
env = Env(BASE_DIR / '.env')

###############
#    Basic    #
###############

#: A list of host/domain names that this site can serve.
#: See :setting:`ALLOWED_HOSTS`.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', [
    '127.0.0.1', '0.0.0.0', 'localhost', '[::1]',
    # From https://stackoverflow.com/questions/9626535/#36609868
    env['DOMAIN'].split('//')[-1].split('/')[0].split('?')[0]
])

#: | A boolean that turns debug mode on/off. See :setting:`DEBUG`.
#: | **SECURITY WARNING: never turn this on in production!**
DEBUG = env.bool('MANGADV_DEBUG', False)

#: | A secret key used to provide cryptographic signing.
#:   See :setting:`SECRET_KEY`.
#: | **SECURITY WARNING: this must be kept secret!**
SECRET_KEY = env.secret('SECRET_KEY')

#: The ID of the current site. See :setting:`SITE_ID`.
SITE_ID = 1

#####################
#    Application    #
#####################

#: A list of strings designating all applications
#: that are enabled in this Django installation.
#: See :setting:`INSTALLED_APPS`.
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

#: A list of middleware to use. See :setting:`MIDDLEWARE`.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'MangAdventure.middleware.BaseMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

#: A string representing the full Python import path to the root URLconf.
#: See :setting:`ROOT_URLCONF`
ROOT_URLCONF = 'MangAdventure.urls'

#: A list containing the settings for all template engines to be used.
#: See :setting:`TEMPLATES`.
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'config.context_processors.extra_settings',
    ]},
    'DIRS': [BASE_DIR / 'MangAdventure' / 'templates'],
    'APP_DIRS': True,
}]

#: The full Python path of the WSGI application
#: object that Django's built-in servers will use.
#: See :setting:`WSGI_APPLICATION`.
WSGI_APPLICATION = 'MangAdventure.wsgi.application'

#: Default primary key field type to use.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

##################
#    Database    #
##################

#: Database settings dictionary. See :setting:`DATABASES`.
DATABASES = {'default': env.db('DB_URL', 'sqlite:///db.sqlite3')}

##################################
#    Logging & Error Handling    #
##################################

#: Subject prefix for email messages sent to admins/managers.
#: See :setting:`EMAIL_SUBJECT_PREFIX`.
EMAIL_SUBJECT_PREFIX = f'[{env["DOMAIN"]}] '

#: URLs that should be ignored when reporting HTTP 404 errors.
#: See :setting:`IGNORABLE_404_URLS`.
IGNORABLE_404_URLS = [
    re.compile(r'^/favicon.ico'),
    re.compile(r'^/robots.txt'),
    re.compile(r'^/api'),
]

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

#: Logging configuration dictionary. See :setting:`LOGGING`.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {pathname}'
                      ' {funcName}:{lineno} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} {module} {funcName} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': LOGS_DIR / 'debug.log',
            'formatter': 'verbose',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'formatter': 'simple',
        },
        'query': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': LOGS_DIR / 'queries.log',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['debug', 'error'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['query'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

##############################
#    Static & Media Files    #
##############################

#: URL that handles the files served from :const:`STATIC_ROOT`.
#: See :setting:`STATIC_URL`.
STATIC_URL = '/static/'

#: Absolute filesystem path to the directory that will hold static files.
#: See :setting:`STATIC_ROOT`.
STATIC_ROOT = BASE_DIR / 'static'

#: A list of directories containing static files.
#: See :setting:`STATICFILES_DIRS`.
STATICFILES_DIRS = [
    ('styles', str(STATIC_ROOT / 'styles')),
    ('scripts', str(STATIC_ROOT / 'scripts')),
    ('COMPILED', str(STATIC_ROOT / 'COMPILED')),
    ('extra', str(STATIC_ROOT / 'extra')),
    ('vendor', str(STATIC_ROOT / 'vendor')),
]

#: URL that handles the media served from :const:`MEDIA_ROOT`.
#: See :setting:`MEDIA_URL`.
MEDIA_URL = '/media/'

#: Absolute filesystem path to the directory that will hold user-uploaded files.
#: See :setting:`MEDIA_ROOT`.
MEDIA_ROOT = BASE_DIR / 'media'

##############################
#    Internationalization    #
##############################

#: Enable Django's translation system. See :setting:`USE_I18N`.
#:
#: .. admonition:: TODO
#:    :class: warning
#:
#:    This is not enabled yet.
USE_I18N = False

#: Enable localized formatting of data. See :setting:`USE_L10N`.
USE_L10N = True

#: Enable timezone-aware datetimes. See :setting:`USE_TZ`.
USE_TZ = True

#: A string representing the language code for this installation.
#: See :setting:`LANGUAGE_CODE`.
LANGUAGE_CODE = env.get('LANG_CODE', 'en-us')

#: The name of the cookie to use for the language cookie.
#: See :setting:`LANGUAGE_COOKIE_NAME`.
LANGUAGE_COOKIE_NAME = 'mangadv_lang'

#: Set the ``HttpOnly`` flag on the language cookie.
#: See :setting:`LANGUAGE_COOKIE_HTTPONLY`.
LANGUAGE_COOKIE_HTTPONLY = True

#: Prevent the language cookie from being sent in cross-site requests.
#: See :setting:`LANGUAGE_COOKIE_SAMESITE`.
LANGUAGE_COOKIE_SAMESITE = 'Strict'

#: A list of all available languages. See :setting:`LANGUAGES`.
LANGUAGES = [
    ('en', 'English'),
]

#: The time zone of this installation. See :setting:`TIME_ZONE`.
TIME_ZONE = env.get('TIME_ZONE', 'UTC')

#########################
#    Users & E-mails    #
#########################

#: A list of validators that are used to check the strength of
#: users' passwords. See :setting:`AUTH_PASSWORD_VALIDATORS`.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'django.contrib.auth.password_validation.{n}Validator'}
    for n in ('UserAttributeSimilarity', 'MinimumLength',
              'CommonPassword', 'NumericPassword')
]

#: A list of authentication backends to use when authenticating a user.
#: See :setting:`AUTHENTICATION_BACKENDS`.
AUTHENTICATION_BACKENDS = [
    'users.backends.ScanlationBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

#: The account adapter class to use.
#: See :auth:`ACCOUNT_ADAPTER <configuration.html>`.
ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'

#: A callable that returns the display name of the user.
#: See :auth:`ACCOUNT_USER_DISPLAY <configuration.html>`.
ACCOUNT_USER_DISPLAY = 'users.get_user_display'

#: The user is required to hand over an e-mail address when signing up.
#: See :auth:`ACCOUNT_EMAIL_REQUIRED <configuration.html>`.
ACCOUNT_EMAIL_REQUIRED = True

#: Use either the username or the email to login.
#: See :auth:`ACCOUNT_AUTHENTICATION_METHOD <configuration.html>`.
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

#: The user is blocked from logging in until the email address is verified.
#: See :auth:`ACCOUNT_EMAIL_VERIFICATION <configuration.html>`.
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

#: The social account adapter class to use.
#: See :auth:`SOCIALACCOUNT_ADAPTER <configuration.html>`.
SOCIALACCOUNT_ADAPTER = 'users.adapters.SocialAccountAdapter'

#: An email address is not required for social accounts.
#: See :auth:`SOCIALACCOUNT_EMAIL_REQUIRED <configuration.html>`.
SOCIALACCOUNT_EMAIL_REQUIRED = False

#: Verifying the email address is not required for social accounts.
#: See :auth:`SOCIALACCOUNT_EMAIL_VERIFICATION <configuration.html>`.
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'

#: Social account provider customization. See
#: :auth:`Google <providers.html#google>`,
#: :auth:`Reddit <providers.html#reddit>`,
#: :auth:`Discord <providers.html#discord>`.
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

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

#: The URL where requests are redirected for login.
#: See :setting:`LOGIN_URL`.
LOGIN_URL = '/user/login'

#: The age of session cookies (1 month).
#: See :setting:`SESSION_COOKIE_AGE`.
SESSION_COOKIE_AGE = 2592000

#: Set the ``HttpOnly`` flag on the session cookie.
#: See :setting:`SESSION_COOKIE_HTTPONLY`.
SESSION_COOKIE_HTTPONLY = True

#: Don't expire the session when the user closes their browser.
#: See :setting:`SESSION_EXPIRE_AT_BROWSER_CLOSE`.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Set up the e-mail server URL.
vars().update(env.email('EMAIL_URL'))

#: The default e-mail address of the site.
#: See :setting:`DEFAULT_FROM_EMAIL`.
DEFAULT_FROM_EMAIL = env['EMAIL_ADDRESS']

##################
#    Security    #
##################

#: List of User-Agents that are not allowed to visit any page.
#: See :setting:`DISALLOWED_USER_AGENTS`.
DISALLOWED_USER_AGENTS = [re.compile(re.escape(b), re.I) for b in BOTS]
DISALLOWED_USER_AGENTS.append(re.compile('^$'))  # empty UA

#: Prevent the session cookie from being sent in cross-site requests.
#: See :setting:`SESSION_COOKIE_SAMESITE`.
SESSION_COOKIE_SAMESITE = 'Strict'

if env.bool('HTTPS', True):
    env.ENV['wsgi.url_scheme'] = 'https'
    MIDDLEWARE.append('MangAdventure.middleware.PreloadMiddleware')

    #: HTTP header/value combination that signifies a secure request.
    #: See :setting:`SECURE_PROXY_SSL_HEADER`.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    #: Redirect all non-HTTPS requests to HTTPS.
    #: See :setting:`SECURE_SSL_REDIRECT`.
    SECURE_SSL_REDIRECT = True

    #: Set the ``X-Content-Type-Options: nosniff`` header.
    #: See :setting:`SECURE_CONTENT_TYPE_NOSNIFF`.
    SECURE_CONTENT_TYPE_NOSNIFF = True

    #: Instructs the browser to send only the origin, not the full URL,
    #: and to send no referrer when a protocol downgrade occurs.
    #: See :setting:`SECURE_REFERRER_POLICY`.
    SECURE_REFERRER_POLICY = 'strict-origin'

    #: Use a secure cookie for the language cookie.
    #: See :setting:`LANGUAGE_COOKIE_SECURE`.
    LANGUAGE_COOKIE_SECURE = True

    #: Use a secure cookie for the session cookie.
    #: See :setting:`SESSION_COOKIE_SECURE`.
    SESSION_COOKIE_SECURE = True

    #: The default protocol used when generating account URLs.
    #: See :auth:`ACCOUNT_DEFAULT_HTTP_PROTOCOL <configuration.html>`.
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Optional django-csp module
if find_spec('csp'):
    #: Set the :csp:`default-src` CSP directive.
    CSP_DEFAULT_SRC = ("'none'",)

    #: Set the :csp:`connect-src` CSP directive.
    CSP_CONNECT_SRC = ("'self'",)

    #: Set the :csp:`script-src` CSP directive.
    CSP_SCRIPT_SRC = ("'self'",)

    #: Set the :csp:`style-src` CSP directive.
    CSP_STYLE_SRC = (
        "'self'", "https://fonts.googleapis.com", "https://cdn.statically.io"
    )

    #: Set the :csp:`font-src` directive.
    CSP_FONT_SRC = (
        "'self'", "https://fonts.gstatic.com", "https://cdn.statically.io"
    )

    #: Set the :csp:`img-src` CSP directive.
    CSP_IMG_SRC = ("'self'", "https://cdn.statically.io")

    #: Set the :csp:`form-action` CSP directive.
    CSP_FORM_ACTION = ("'self'",)

    #: Set the :csp:`frame-src` CSP directive.
    CSP_FRAME_SRC = ("'self'",)

    #: Set the :csp:`frame-ancestors` CSP directive.
    CSP_FRAME_ANCESTORS = ("'self'",)

    #: Set the :csp:`base-uri` CSP directive.
    CSP_BASE_URI = ("'none'",)

    #: Set the :csp:`report-uri` CSP directive.
    CSP_REPORT_URI = env.list('CSP_REPORT_URI')

    if CSP_REPORT_URI:
        MIDDLEWARE.append('csp.contrib.rate_limiting.RateLimitedCSPMiddleware')

        #: Percentage of requests that should see the ``report-uri`` directive.
        CSP_REPORT_PERCENTAGE = env.float('CSP_REPORT_PERCENTAGE', 1.0) / 100
    else:
        MIDDLEWARE.append('csp.middleware.CSPMiddleware')

    #: URLs beginning with any of these will not get the CSP headers.
    CSP_EXCLUDE_URL_PREFIXES = (
        '/api', '/admin-panel', '/robots.txt',
        '/opensearch.xml', '/contribute.json',
    )

#############
#    API    #
#############

#: Configuration for the API.
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.v2.pagination.DummyPagination',
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
    'DEFAULT_THROTTLE_RATES': {'anon': '200/m'},
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
    'PAGE_SIZE': env.int('API_PAGE_SIZE', 25),
}
if not DEBUG:  # pragma: no cover
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

#######################
#    Configuration    #
#######################

#: Configuration variables defined by the user in the ``.env`` file.
CONFIG = {
    'NAME': env['NAME'],
    'DOMAIN': env['DOMAIN'],
    'DESCRIPTION': env['DESCRIPTION'],
    'KEYWORDS': env['KEYWORDS'],
    'DISCORD': env.get('DISCORD'),
    'TWITTER': env.get('TWITTER'),
    'FAVICON': env['FAVICON'],
    'LOGO': env['LOGO'],
    'MAIN_BG_COLOR': env['MAIN_BG_COLOR'],
    'MAIN_TEXT_COLOR': env['MAIN_TEXT_COLOR'],
    'ALTER_BG_COLOR': env['ALTER_BG_COLOR'],
    'ALTER_TEXT_COLOR': env['ALTER_TEXT_COLOR'],
    'SHADOW_COLOR': env['SHADOW_COLOR'],
    'FONT_NAME': env['FONT_NAME'],
    'FONT_URL': env['FONT_URL'],
    'USE_CDN': env.bool('USE_CDN', True),
    'ALLOW_DLS': env.bool('ALLOW_DLS', True),
    'MAX_RELEASES': env.int('MAX_RELEASES', 10),
    'MAX_CHAPTERS': env.int('MAX_CHAPTERS', 1),
    'SHOW_CREDITS': env.bool('SHOW_CREDITS', True),
    'ENABLE_API_V1': env.bool('ENABLE_API_V1', False),
}

CONFIG['LOGO_TW'] = env.get('LOGO_TW', CONFIG['LOGO'])
CONFIG['LOGO_OG'] = env.get('LOGO_OG', CONFIG['LOGO'])

###############
#    Debug    #
###############

if DEBUG:
    INTERNAL_IPS = env.list('INTERNAL_IPS', ['127.0.0.1'])
    ALLOWED_HOSTS += [f'192.168.1.{i}' for i in range(2, 256)]
    if find_spec('debug_toolbar'):
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        TEMPLATES[0]['OPTIONS']['context_processors'].append(
            'django.template.context_processors.debug'
        )

################
#    Sentry    #
################

if find_spec('sentry_sdk'):
    from sentry_sdk.hub import init as sentry_init
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_init(
        debug=DEBUG,
        dsn=env['SENTRY_DSN'],
        send_default_pii=True,
        release=f'mangadventure@{VERSION}',
        integrations=[DjangoIntegration()],
        traces_sample_rate=env.float('SENTRY_SAMPLE_RATE', 0.0) / 100
    )

del BOTS, LOGS_DIR, VERSION

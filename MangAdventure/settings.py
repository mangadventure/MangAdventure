import re
from os import mkdir, path

from yaenv import Env

from . import __version__ as VERSION
from .bad_bots import BOTS

# Build paths inside the project like this: path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

# Load environment variables from .env file.
env = Env(path.join(BASE_DIR, '.env'))

###############
#    Basic    #
###############

# A list of host/domain names that this site can serve.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', [
    '127.0.0.1', '0.0.0.0', 'localhost', '[::1]',
    # From https://stackoverflow.com/questions/9626535/#36609868
    env['DOMAIN'].split('//')[-1].split('/')[0].split('?')[0]
])

# A boolean that turns debug mode on/off.
# SECURITY WARNING: never turn this on in production!
DEBUG = env.bool('MANGADV_DEBUG', False)

# A secret key used to provide cryptographic signing.
# SECURITY WARNING: this must be kept secret!
SECRET_KEY = env.secret('SECRET_KEY')

# The ID of the current site.
SITE_ID = 1

#####################
#    Application    #
#####################

# A list of strings designating all applications
# that are enabled in this Django installation.
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
    'user_comments',
    'config',
    'reader',
    'api',
    'groups',
    'users',
]

# A list of middleware to use.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

# A string representing the full Python import path to the root URLconf.
ROOT_URLCONF = 'MangAdventure.urls'

# A list containing the settings for all template engines to be used.
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.template.context_processors.media',
        'django.contrib.messages.context_processors.messages',
        'config.context_processors.extra_settings',
    ]},
    'DIRS': [path.join(BASE_DIR, 'MangAdventure', 'templates')],
    'APP_DIRS': True,
}]

# The full Python path of the WSGI application
# object that Django's built-in servers will use.
WSGI_APPLICATION = 'MangAdventure.wsgi.application'

##################
#    Database    #
##################

# Database settings dictionary.
DATABASES = {'default': env.db('DB_URL', 'sqlite:///db.sqlite3')}

##################################
#    Logging & Error Handling    #
##################################

# Subject prefix for email messages sent to admins/managers.
EMAIL_SUBJECT_PREFIX = '[%s] ' % env['DOMAIN']

# URLs that should be ignored when reporting HTTP 404 errors.
IGNORABLE_404_URLS = [
    re.compile(r'^/favicon.ico'),
    re.compile(r'^/robots.txt'),
    re.compile(r'^/api'),
]

LOGS_DIR = path.join(BASE_DIR, 'logs')
if not path.exists(LOGS_DIR): mkdir(LOGS_DIR)

# Logging configuration dictionary.
LOGGING = {  # TODO: better logging
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'}
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(pathname)s'
                      ' %(funcName)s:%(lineno)s %(message)s',
        },
        'simple': {
            'format': '%(asctime)s %(module)s %(funcName)s %(message)s',
        },
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': path.join(LOGS_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': path.join(LOGS_DIR, 'errors.log'),
            'formatter': 'simple',
        },
        'query': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': path.join(LOGS_DIR, 'queries.log'),
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

# URL that handles the files served from STATIC_ROOT.
STATIC_URL = '/static/'

# Absolute filesystem path to the directory that will hold static files.
STATIC_ROOT = path.join(BASE_DIR, 'static')

# A list of directories containing static files.
STATICFILES_DIRS = [
    ('styles', path.join(STATIC_ROOT, 'styles')),
    ('scripts', path.join(STATIC_ROOT, 'scripts')),
    ('COMPILED', path.join(STATIC_ROOT, 'COMPILED')),
]

# A list of static file finder backends.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = path.join(BASE_DIR, 'media')

##############################
#    Internationalization    #
##############################

# Enable Django's translation system.
USE_I18N = False  # TODO: enable this

# Enable localized formatting of data.
USE_L10N = True

# Enable timezone-aware datetimes.
USE_TZ = True

# A string representing the language code for this installation.
LANGUAGE_CODE = env.get('LANG_CODE', 'en-us')

# The name of the cookie to use for the language cookie.
LANGUAGE_COOKIE_NAME = 'mangadv_lang'

# A list of all available languages.
LANGUAGES = [
    ('en', 'English'),
]

# The time zone for this installation.
TIME_ZONE = env.get('TIME_ZONE', 'UTC')

#########################
#    Users & E-mails    #
#########################

# A list of validators that are used to check the strength of users' passwords.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.%sValidator' % n}
    for n in ('UserAttributeSimilarity', 'MinimumLength',
              'CommonPassword', 'NumericPassword')
]

# A list of authentication backends to use when authenticating a user.
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

# The account adapter class to use.
ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'

# A callable that returns the display name of the user.
ACCOUNT_USER_DISPLAY = 'users.get_user_display'

# The user is required to hand over an e-mail address when signing up.
ACCOUNT_EMAIL_REQUIRED = True

# Use either the username or the email to login.
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# The user is blocked from logging in until the email address is verified.
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# The social account adapter class to use.
SOCIALACCOUNT_ADAPTER = 'users.adapters.SocialAccountAdapter'

# An email address is not required for social accounts.
SOCIALACCOUNT_EMAIL_REQUIRED = False

# Verifying the email address is not required for social accounts.
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'

# Social account provider customization.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    'reddit': {
        'AUTH_PARAMS': {'duration': 'permanent'},
        'USER_AGENT': 'Django:MangAdventure:{} (by {})'.format(
            VERSION, 'https://github.com/mangadventure'
        ),
    },
    'discord': {
        'SCOPE': ['identify', 'email'],
    }
}

# The URL where requests are redirected for login.
LOGIN_URL = '/user/login'

# The age of session cookies (1 month).
SESSION_COOKIE_AGE = 2592000

# Use HttpOnly flag on the session cookie.
SESSION_COOKIE_HTTPONLY = True

# Don't expire the session when the user closes their browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Sets up the e-mail server URL.
vars().update(env.email('EMAIL_URL'))

# The default e-mail address of the site.
DEFAULT_FROM_EMAIL = env['EMAIL_ADDRESS']

##################
#    Security    #
##################

# List of User-Agents that are not allowed to visit any page.
DISALLOWED_USER_AGENTS = [re.compile(re.escape(b), re.I) for b in BOTS]
DISALLOWED_USER_AGENTS.append(re.compile('^$'))  # empty UA

# Use HttpOnly flag on the CSRF cookie.
CSRF_COOKIE_HTTP_ONLY = True

if env.bool('HTTPS', True):
    env.ENV['wsgi.url_scheme'] = 'https'
    MIDDLEWARE.append('MangAdventure.middleware.PreloadMiddleware')

    # HTTP header/value combination that signifies a request is secure.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Redirect all non-HTTPS requests to HTTPS.
    SECURE_SSL_REDIRECT = True

    # Sets the "X-XSS-Protection: 1; mode=block" header.
    SECURE_BROWSER_XSS_FILTER = True

    # Sets the "X-Content-Type-Options: nosniff" header.
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Use a secure cookie for the session cookie.
    SESSION_COOKIE_SECURE = True

    # Use a secure cookie for the CSRF cookie.
    CSRF_COOKIE_SECURE = True

    # The default protocol used when generating account URLs.
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Optional django-csp module
try:
    __import__('csp.middleware')
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')
except ImportError:
    pass
else:
    # Sets the default-src directive.
    CSP_DEFAULT_SRC = ("'none'",)

    # Sets the connect-src directive.
    CSP_CONNECT_SRC = ("'self'",)

    # Sets the script-src directive.
    CSP_SCRIPT_SRC = ("'self'", "https://cdn.tinymce.com")

    # Sets the style-src directive.
    CSP_STYLE_SRC = (
        "'self'", "https://fonts.googleapis.com", "https://cdn.staticaly.com"
    )

    # Sets the font-src directive.
    CSP_FONT_SRC = (
        "'self'", "https://fonts.gstatic.com", "https://cdn.staticaly.com"
    )

    # Sets the img-src directive.
    CSP_IMG_SRC = ("'self'",)

    # Sets the form-action directive.
    CSP_FORM_ACTION = ("'self'",)

    # Sets the frame-src directive.
    CSP_FRAME_SRC = ("'self'",)

    # Sets the frame-ancestors directive.
    CSP_FRAME_ANCESTORS = ("'self'",)

    # Sets the base-uri directive.
    CSP_BASE_URI = ("'none'",)

    # Sets the report-uri directive.
    CSP_REPORT_URI = env.list('CSP_REPORT_URI')

    # URLs beginning with any of these will not get the CSP headers.
    CSP_EXCLUDE_URL_PREFIXES = (
        '/api', '/admin-panel', '/robots.txt',
        '/opensearch.xml', '/contribute.json',
    )

#######################
#    Configuration    #
#######################

# Configuration variables defined by the user.
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
    'MAX_RELEASES': env.int('MAX_RELEASES', 10),
    'MAX_CHAPTERS': env.int('MAX_CHAPTERS', 1),
    'SHOW_CREDITS': env.bool('SHOW_CREDITS', True),
}

##################
#    Comments    #
##################

# The app used for custom comments.
COMMENTS_APP = 'users'

# Removed comments won't be hidden.
COMMENTS_HIDE_REMOVED = False

# Allow HTML in comments.
COMMENTS_ALLOW_HTML = True

# Use TinyMCE widget in comments.
COMMENTS_WIDGET = 'users.widgets.TinyMCEComment'

###############
#    Debug    #
###############

if DEBUG:
    INTERNAL_IPS = env.list('INTERNAL_IPS', ['127.0.0.1'])
    ALLOWED_HOSTS += ['192.168.1.%s' % i for i in range(2, 256)]
    try:
        __import__('debug_toolbar')
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        TEMPLATES[0]['OPTIONS']['context_processors'].append(
            'django.template.context_processors.debug'
        )
    except ImportError:
        pass

del BOTS, LOGS_DIR, VERSION

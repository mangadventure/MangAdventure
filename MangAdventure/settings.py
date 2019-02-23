from __future__ import print_function
from django.core.management.color import color_style as style
from os import path, mkdir, environ as env
from re import compile as regex, IGNORECASE
from sys import stderr, argv
from config import read_config, write_config
from .bad_bots import BOTS
from . import __version__ as VERSION


def warn(msg): print(style().WARNING('WARNING: ' + msg), file=stderr)


CONFIG = read_config()

###############
#    Basic    #
###############

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

try:
    # A secret key used to provide cryptographic signing.
    # SECURITY WARNING: this must be kept secret!
    SECRET_KEY = CONFIG['secret_key']
    if not SECRET_KEY:
        raise KeyError
except KeyError:
    SECRET_KEY = env.get('SECRET_KEY', ''.join(
        __import__('random').SystemRandom().choice(
            'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        ) for i in range(50)
    ))
    write_config('secret_key', SECRET_KEY)

# A boolean that turns debug mode on/off.
# SECURITY WARNING: never turn this on in production!
DEBUG = (env.get('MANGADV_DEBUG', 'false').lower() == 'true')

# A list of host/domain names that this site can serve.
ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost', '[::1]']
if DEBUG:
    ALLOWED_HOSTS += ['192.168.1.%s' % i for i in range(2, 256)]
try:
    # From https://stackoverflow.com/questions/9626535/#36609868
    BASE_URL = CONFIG['site_url'].split('//')[-1].split('/')[0].split('?')[0]
    if BASE_URL:
        ALLOWED_HOSTS += ['.' + BASE_URL]
    else:
        raise KeyError
except KeyError:
    if 'configureurl' not in argv:
        warn("You should configure your website's URL "
             "by running the 'configureurl' command.")

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
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'static_precompiler',
    'constance.backends.database',
    'config.apps.SiteConfig',
    'next_prev',
    'config',
    'reader',
    'api',
    'groups',
]

# A list of middleware to use.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'MangAdventure.middleware.XPBMiddleware',
]

# A string representing the full Python import path to the root URLconf.
ROOT_URLCONF = 'MangAdventure.urls'

CONTEXT_PROCESSORS = [
    'constance.context_processors.config',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'config.context_processors.extra_settings',
]
if DEBUG:
    CONTEXT_PROCESSORS += ['django.template.context_processors.debug']

# A list containing the settings for all template engines to be used.
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'context_processors': CONTEXT_PROCESSORS},
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
DATABASES = {  # TODO: add MySQL support
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),
    }
}

##################################
#    Logging & Error Handling    #
##################################

# Subject prefix for email messages sent to admins/managers.
EMAIL_SUBJECT_PREFIX = '[%s] ' % CONFIG.get('site_url', 'MangAdventure')

# URLs that should be ignored when reporting HTTP 404 errors.
IGNORABLE_404_URLS = [
    regex(r'^/favicon.ico'),
    regex(r'^/robots.txt'),
    regex(r'^/api'),
]

LOGS_DIR = path.join(BASE_DIR, 'logs')
if not path.exists(LOGS_DIR):
    mkdir(LOGS_DIR)


# Logging configuration dictionary.
LOGGING = {  # TODO: better logging
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'}
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': path.join(LOGS_DIR, 'debug.log')
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_false'],
            'filename': path.join(LOGS_DIR, 'errors.log')
        },
    },
    'loggers': {
        'django': {
            'handlers': ['debug', 'error'],
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
STATIC_ROOT = path.join(BASE_DIR, 'static/')

# A list of static file finder backends.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
]

# List of enabled compilers for django-static-precompiler.
STATIC_PRECOMPILER_COMPILERS = [
    ('static_precompiler.compilers.libsass.SCSS', {
        'sourcemap_enabled': False,
        'precision': 7,
        'load_paths': [path.join(STATIC_ROOT, 'styles')],
        'output_style': 'compressed',
    }),
]

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = path.join(BASE_DIR, 'media/')

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
LANGUAGE_CODE = 'en-us'  # TODO: make this configurable

# The name of the cookie to use for the language cookie.
LANGUAGE_COOKIE_NAME = 'mangadv_lang'

# A list of all available languages.
LANGUAGES = [
    ('en', 'English'),
]

# The time zone for this installation.
TIME_ZONE = 'UTC'  # TODO: make this configurable

#######################
#    Users & Email    #
#######################

# A list of validators that are used to check the strength of users' passwords.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.%sValidator' % n}
    for n in ['UserAttributeSimilarity', 'MinimumLength',
              'CommonPassword', 'NumericPassword']
]

# A list of authentication backends to use when authenticating a user.
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# The account adapter class to use.
ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'

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
    'reddit': {
        'AUTH_PARAMS': {'duration': 'permanent'},
        'USER_AGENT': 'Django:MangAdventure:{} ({})'.format(
            VERSION, 'https://github.com/mangadventure/MangAdventure'
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

# Don't expire the session when the user closes their browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

try:
    # Use a secure TLS connection when talking to the SMTP server.
    EMAIL_USE_TLS = True

    # The host to use for sending email.
    EMAIL_HOST = CONFIG['smtp_host']

    # Username to use for the SMTP server defined in EMAIL_HOST.
    EMAIL_HOST_USER = CONFIG['smtp_user']

    # Password to use for the SMTP server defined in EMAIL_HOST.
    EMAIL_HOST_PASSWORD = CONFIG['smtp_pass']

    # Port to use for the SMTP server defined in EMAIL_HOST.
    EMAIL_PORT = CONFIG['smtp_port']

    # Default email address to use for various
    # automated correspondence from the site manager(s).
    DEFAULT_FROM_EMAIL = CONFIG['smtp_mail']

    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER,
                EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL]):
        raise KeyError
    INSTALLED_APPS += [
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.reddit',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.discord',
        'users',
    ]
except KeyError:
    if 'configuresmtp' not in argv:
        warn("To enable the User module, you have to configure your SMTP "
             "mail server's settings via the 'configuresmtp' command.")

##################
#    Security    #
##################

# List of User-Agents that are not allowed to visit any page.
DISALLOWED_USER_AGENTS = [regex(bot, IGNORECASE) for bot in BOTS]

# Use HttpOnly flag on the CSRF cookie
CSRF_COOKIE_HTTP_ONLY = True

env.setdefault('HTTPS', CONFIG.get('https', 'on'))
if env.get('HTTPS').lower() == 'on':
    env['wsgi.url_scheme'] = 'https'

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

    # The default protocol used for when generating account URLs.
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Optional django-csp module
try:
    __import__('csp.middleware')
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')

    # Sets the default-src directive.
    CSP_DEFAULT_SRC = ("'none'",)

    # Sets the script-src directive.
    CSP_SCRIPT_SRC = ("'self'",)

    # Sets the style-src directive.
    CSP_STYLE_SRC = (
        "'self'", "https://fonts.googleapis.com", "https://cdn.staticaly.com",
    )

    # Sets the font-src directive.
    CSP_FONT_SRC = (
        "'self'", "https://fonts.gstatic.com", "https://cdn.staticaly.com",
    )

    # Sets the img-src directive.
    CSP_IMG_SRC = ("'self'",)

    # Sets the object-src directive.
    CSP_OBJECT_SRC = ("'self'",)

    # Sets the frame-src directive.
    CSP_FRAME_SRC = ("'self'",)

    # Sets the frame-ancestors directive.
    CSP_FRAME_ANCESTORS = ("'self'",)

    # Sets the base-uri directive.
    CSP_BASE_URI = ("'none'",)

    # URLs beginning with any of these will not get the CSP headers.
    CSP_EXCLUDE_URL_PREFIXES = ('/api', '/admin')
except ImportError:
    pass

##########################
#    django-constance    #
##########################

# Custom constance field types.
CONSTANCE_ADDITIONAL_FIELDS = {
    'char': ('django.forms.CharField', {}),
    'url': ('django.forms.URLField', {}),
    'color': ('MangAdventure.forms.ColorField', {}),
    'number': ('django.forms.IntegerField', {
        'min_value': 1,
    }),
    'discord': ('MangAdventure.forms.DiscordURLField', {
        'required': False
    }),
    'twitter': ('MangAdventure.forms.TwitterField', {
        'required': False
    }),
    'desc': ('django.forms.CharField', {
        'max_length': 250, 'widget': 'django.forms.Textarea'
    }),
    'logo': ('MangAdventure.forms.SVGImageField', {}),
    'favicon': ('django.forms.ImageField', {})
}

# Constance configuration variables.
CONSTANCE_CONFIG = {
    'NAME': (
        'MangAdventure', 'The name of your website.', 'char'
    ),
    'DESCRIPTION': (
        'MangAdventure is a simple manga hosting CMS written in Django',
        'A description for your website.', 'desc'
    ),
    'KEYWORDS': (
        'mangadventure,manga,scanlation,reader',
        'A comma-separated list of keywords that describe your website', 'char'
    ),
    'DISCORD': (
        '', 'The Discord server of your group.', 'discord'
    ),
    'TWITTER': (
        '', 'The Twitter username of your group.', 'twitter'
    ),
    'FAVICON': (
        '', 'The favicon of your website.', 'favicon'
    ),
    'MAIN_BACKGROUND': (
        '#ffffff', 'The main background color of your website.', 'color'
    ),
    'ALTER_BACKGROUND': (
        '#aaaaaa', 'The alternate background color of your website.', 'color'
    ),
    'MAIN_TEXT_COLOR': (
        '#000000', 'The main text color of your website.', 'color'
    ),
    'ALTER_TEXT_COLOR': (
        '#555555', 'The alternate text color of your website.', 'color'
    ),
    'SHADOW_COLOR': (
        '#444444', 'The shadow color of your website.', 'color'
    ),
    'FONT_URL': (
        'https://fonts.googleapis.com/css?family=Lato',
        'The URL of the font to be used in your website.', 'url'
    ),
    'FONT_NAME': (
        'Lato', 'The name of the font that '
        'corresponds to the above URL.', 'char'
    ),
    'LOGO_LARGE': (
        '', 'Upload a large-sized logo for your website.', 'logo'
    ),
    'LOGO_MEDIUM': (
        '', 'Upload a medium-sized logo for your website.', 'logo'
    ),
    'LOGO_SMALL': (
        '', 'Upload a small-sized logo for your website.', 'logo'
    ),
    'MAX_RELEASES': (
        10, 'The maximum number of releases to '
        'be shown in the main page', 'number'
    ),
    'MAX_CHAPTERS': (
        1, 'The maximum number of chapters to be shown '
        'for each series in the reader page.', 'number'
    ),
    'SHOW_CREDITS': (
        True, "Credit MangAdventure in the site's footer.", bool
    )
}

# Constance configuration groups.
CONSTANCE_CONFIG_FIELDSETS = {
    'Site Settings': (
        'NAME', 'DESCRIPTION', 'KEYWORDS',
        'FAVICON', 'TWITTER', 'DISCORD',
    ),
    'Theme Settings': (
        'MAIN_BACKGROUND', 'ALTER_BACKGROUND', 'MAIN_TEXT_COLOR',
        'ALTER_TEXT_COLOR', 'SHADOW_COLOR', 'FONT_URL', 'FONT_NAME',
    ),
    'Logo Settings': (
        'LOGO_LARGE', 'LOGO_MEDIUM', 'LOGO_SMALL',
    ),
    'Other Settings': (
        'MAX_RELEASES', 'MAX_CHAPTERS', 'SHOW_CREDITS',
    )
}

# Use the database for storing configuration.
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

del CONFIG, BOTS, IGNORECASE, VERSION, CONTEXT_PROCESSORS


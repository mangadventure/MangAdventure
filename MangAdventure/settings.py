from django.core.management.color import color_style as style
from os import path, mkdir, environ as env
from re import compile as reg, IGNORECASE
from sys import stderr, argv
from . import __version__ as ver
from settings import CONFIG

# From https://stackoverflow.com/questions/9626535/#36609868
get_domain = lambda url: url.split('//')[-1].split('/')[0].split('?')[0]

print_err = lambda msg: print(style().ERROR('ERROR: ' + msg), file=stderr)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
_settings = path.dirname(path.abspath(__file__))
BASE_DIR = path.dirname(_settings)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY = CONFIG['settings']['secret_key']
    if not SECRET_KEY:
        raise KeyError
except KeyError:
    SECRET_KEY = 'm-4!(a(2a9w5q@n07#_aup4j^mox$e#+brgd51_5xdbg6u3i)x'
    if 'generatekey' not in argv:
        print_err("You must first generate a secret key "
                  "by running the 'generatekey' command.")
        exit(2)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.get('MANGADV_DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = [
    '127.0.0.1', '0.0.0.0',
    'localhost', '[::1]',
]
try:
    BASE_URL = get_domain(CONFIG['settings']['site_url'])
    if BASE_URL:
        ALLOWED_HOSTS += [BASE_URL, 'www.' + BASE_URL]
    else:
        raise KeyError
except KeyError:
    if 'generatekey' not in argv and 'configureurl' not in argv:
        print_err("You must configure your website's URL "
                  "by running the 'configureurl' command.")
        exit(2)

_bad_bots = path.join(_settings, 'bad-bots.txt')
DISALLOWED_USER_AGENTS = [
    reg(r'%s' % l.strip(), IGNORECASE) for l in open(_bad_bots)
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'static_precompiler',
    'constance.backends.database',
    'settings.apps.SettingsConfig',
    'next_prev',
    'settings',
    'reader',
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

ROOT_URLCONF = 'MangAdventure.urls'

CONTEXT_PROCESSORS = [
    'constance.context_processors.config',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'settings.context_processors.extra_settings',
]
if DEBUG:
    CONTEXT_PROCESSORS += ['django.template.context_processors.debug']

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'context_processors': CONTEXT_PROCESSORS},
    'APP_DIRS': True, 'DIRS': [path.join(BASE_DIR, 'templates')],
}]

WSGI_APPLICATION = 'MangAdventure.wsgi.application'

# Constance
# https://django-constance.readthedocs.io/en/latest/index.html#configuration

_site = 'The %s of your website.'
_color = 'The %s color of your website.'
_logo = 'Upload a %s-sized logo for your website.'

CONSTANCE_ADDITIONAL_FIELDS = {
    'char': ('django.forms.CharField', {}),
    'url': ('django.forms.URLField', {}),
    'number': ('django.forms.IntegerField', {
        'min_value': 0
    }),
    'color': ('django.forms.CharField', {
        'max_length': 20
    }),
    'twitter': ('django.forms.CharField', {
        'max_length': 15,
    }),
    'desc': ('django.forms.CharField', {
        'max_length': 250,
        'widget': 'django.forms.Textarea'
    }),
    'html': ('django.forms.CharField', {
        'strip': False,
        'widget': 'django.forms.Textarea'
    }),
    'logo': ('reader.modules.forms.SVGImageField', {}),
    'favicon': ('django.forms.ImageField', {})
}
CONSTANCE_CONFIG = {
    'FOOTER': (
        'If you liked any of the manga you read here, '
        'consider buying the original versions to support '
        'the authors.\nThis site was created using <a href='
        '"https://github.com/evangelos-ch/MangAdventure"'
        ' rel="noopener" target="_blank">'
        'MangAdventure v' + ver + '</a>',
        _site % 'footer' + ' HTML allowed.', 'html'
    ),
    'NAME': ('MangAdventure', _site % 'name', 'char'),
    'DESCRIPTION': (
        'MangAdventure is a simple manga '
        'hosting webapp written in Django',
        'A description for your website.', 'desc'
    ),
    'DISCORD': ('N/A', _site % 'Discord server', 'char'),
    'TWITTER': ('N/A', _site % 'Twitter username', 'twitter'),
    'FAVICON': ('', _site % 'favicon', 'favicon'),
    'MAIN_BACKGROUND': ('#FFF', _color % 'main background', 'color'),
    'ALTER_BACKGROUND': ('#AAA', _color % 'alternate background', 'color'),
    'MAIN_TEXT_COLOR': ('#000', _color % 'main text', 'color'),
    'ALTER_TEXT_COLOR': ('#555', _color % 'alternate text', 'color'),
    'FONT_URL': (
        'https://fonts.googleapis.com/css?family=Lato',
        'The URL of the font to be used in your website.', 'url'
    ),
    'FONT_NAME': ('Lato', 'The name of the font that '
                          'corresponds to the above URL.', 'char'),
    'LOGO_LARGE': ('', _logo % 'large', 'logo'),
    'LOGO_MEDIUM': ('', _logo % 'medium', 'logo'),
    'LOGO_SMALL': ('', _logo % 'small', 'logo'),
    'MAX_RELEASES': (10, 'The maximum number of releases '
                         'to be shown in the main page', 'number'),
    'MAX_CHAPTERS': (1, 'The maximum number of chapters '
                        'to be shown for each series '
                        'in the reader page.', 'number')
}
CONSTANCE_CONFIG_FIELDSETS = {
    'Site Settings': (
        'NAME', 'DESCRIPTION', 'FOOTER',
        'DISCORD', 'TWITTER', 'FAVICON'
    ),
    'Theme Settings': (
        'MAIN_BACKGROUND', 'ALTER_BACKGROUND',
        'MAIN_TEXT_COLOR', 'ALTER_TEXT_COLOR',
        'FONT_URL', 'FONT_NAME',
    ),
    'Logo Settings': ('LOGO_LARGE', 'LOGO_MEDIUM', 'LOGO_SMALL'),
    'Other Settings': ('MAX_RELEASES', 'MAX_CHAPTERS')
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

# Debug and Error Logging
# https://docs.djangoproject.com/en/dev/topics/logging/

if not path.exists(path.join(BASE_DIR, 'logs')):
    mkdir(path.join(BASE_DIR, 'logs'))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': path.join(BASE_DIR, 'logs', 'debug.log')
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_false'],
            'filename': path.join(BASE_DIR, 'logs', 'errors.log')
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
STATIC_ROOT = path.join(BASE_DIR, 'static/')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
]
STATIC_PRECOMPILER_COMPILERS = [
    ('static_precompiler.compilers.libsass.SCSS', {
        'sourcemap_enabled': False,
        'precision': 7,
        'load_paths': [path.join(STATIC_ROOT, 'styles')],
        'output_style': 'compressed',
    }),
]

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = path.join(BASE_DIR, 'media/')

# HTTPS
try:
    env['HTTPS'] = CONFIG['settings']['https']
except KeyError:
    env['HTTPS'] = 'off'

if env.get('HTTPS', 'off').lower() == 'on':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    env['wsgi.url_scheme'] = 'https'


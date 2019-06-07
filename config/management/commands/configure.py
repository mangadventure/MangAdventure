from django.core.management import BaseCommand
from django.conf import settings
from os import path, environ as env
from subprocess import call


USER_SETTINGS = """\
# The domain of your website.
SITE_DOMAIN = ''

# Set this to 'on' to enable HTTPS or 'off' to disable it
HTTPS = 'on'

# The host to use for sending e-mails.
SMTP_HOST = 'smtp.gmail.com'

# The port to use for the host defined in smtp_host.
SMTP_PORT = 587

# The default e-mail address of site.
SMTP_MAIL = ''

# The username to use for your e-mail user.
SMTP_USER = ''

# The password to use for your e-mail user.
SMTP_PASS = ''

# The time zone of your server.
TIME_ZONE = 'UTC'

# The language code of your site.
LANG_CODE = 'en-us'
"""


class Command(BaseCommand):
    help = 'Opens a text editor to edit the configuration file.'

    def _get_editor(self):
        system = __import__('platform').system()
        if system == 'Linux':
            editor = 'editor'
        elif system.startswith(('Windows', 'CYGWIN_NT')):
            editor = 'start'
        elif system == 'Darwin':
            editor = 'open'
        else:
            self.stderr.write(self.style.ERROR(
                "ERROR: couldn't detect default editor."
                " Please use '--editor' to specify it."
            ))
            exit(2)
        return editor

    def add_arguments(self, parser):
        parser.add_argument(
            '-e', '--editor', type=str, help='The editor program to use.'
        )

    def handle(self, *args, **options):
        editor = options.get('editor') or \
            env.get('EDITOR', self._get_editor())
        file_path = path.join(
            settings.BASE_DIR, 'MangAdventure', 'user_settings.py'
        )
        if not path.exists(file_path):
            with open(file_path, 'w+') as f:
                f.write(USER_SETTINGS)
        self.stdout.write('Opening your editor...')
        exit(call((editor, file_path)))


from django.core.management import BaseCommand
from getpass import getpass
from sys import stdin, exit
from config import write_config


class Command(BaseCommand):
    help = "Configures the SMTP server settings" \
        " for activation and reset emails."

    def add_arguments(self, parser):
        parser.add_argument('HOST', nargs=1, type=str,
                            help="The host address of the SMTP server. "
                            "You can also specify the port like so: "
                            "'address:port'. The default port is 587.")
        parser.add_argument('USER', nargs=1, type=str,
                            help='The user of the SMTP server.')
        parser.add_argument('--address', nargs=1, type=str,
                            help="The Email address that the Emails will be "
                                 "sent from. Defaults to SMTP_USER@SMTP_HOST.")
        parser.add_argument('--password', nargs=1, type=str,
                            help="The password of the SMTP server's user.")

    def handle(self, *args, **options):
        user = options['USER'][0]
        host = options['HOST'][0].split(':')
        port = host[1] if len(host) > 1 else '587'
        mail = options.get('ADDRESS', '%s@%s' % (user, host[0]))
        password = options.get('PASSWORD', [None])[0]
        if not password:
            if hasattr(stdin, 'isatty') and not stdin.isatty():
                self.stderr.write(self.style.ERROR(
                    "Couldn't get the password because this program is not "
                    "running in a TTY.\nEither run it in a TTY, or use the "
                    "'--password' option to specify the password."
                ))
                exit(3)
            password = getpass('SMTP user password: ')
        write_config('settings', 'smtp_host', host[0])
        write_config('settings', 'smtp_port', port)
        write_config('settings', 'smtp_mail', mail)
        write_config('settings', 'smtp_user', user)
        write_config('settings', 'smtp_pass', password)
        self.stdout.write(self.style.SUCCESS(
            'Saved SMTP settings in config.ini'))


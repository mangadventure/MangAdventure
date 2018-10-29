from django.core.management import BaseCommand
from config import write_config


class Command(BaseCommand):
    help = 'Configures the SMTP server settings for activation and reset emails.'

    def add_arguments(self, parser):
        parser.add_argument('SMTP_HOST', nargs=1, type=str,
                            help='The host address of the SMTP server.')
        parser.add_argument('SMTP_PORT', nargs=1, type=str,
                            help='The port the SMTP server is listening on.')
        parser.add_argument('SMTP_USER', nargs=1, type=str,
                            help='The username / address for the SMTP server.')
        parser.add_argument('SMTP_PASS', nargs=1, type=str,
                            help='The password of the user on the SMTP server.')

    def handle(self, *args, **options):
        write_config('settings', 'smtp_host', *options['SMTP_HOST'])
        write_config('settings', 'smtp_port', *options['SMTP_PORT'])
        write_config('settings', 'smtp_user', *options['SMTP_USER'])
        write_config('settings', 'smtp_pass', *options['SMTP_PASS'])
        self.stdout.write(self.style.SUCCESS('Saved SMTP settings in in config.ini'))


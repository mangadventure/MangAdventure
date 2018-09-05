from django.core.management import BaseCommand
from config import write_config


class Command(BaseCommand):
    help = 'Enables or disables HTTPS'

    def add_arguments(self, parser):
        parser.add_argument('state', choices=['on', 'off'],
                            help='Turn HTTPS on or off')

    def handle(self, *args, **options):
        https = options['state']
        action = 'Enabled' if https == 'on' else 'Disabled'
        write_config('settings', 'https', https)
        self.stdout.write(self.style.SUCCESS('%s HTTPS' % action))


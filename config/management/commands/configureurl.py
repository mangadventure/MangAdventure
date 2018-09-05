from django.core.management import BaseCommand
from config import write_config


class Command(BaseCommand):
    help = 'Configures the URL of your website'

    def add_arguments(self, parser):
        parser.add_argument('URL', nargs=1, type=str,
                            help='The URL of your website')

    def handle(self, *args, **options):
        write_config('settings', 'site_url', *options['URL'])
        self.stdout.write(self.style.SUCCESS('Saved URL in config.ini'))


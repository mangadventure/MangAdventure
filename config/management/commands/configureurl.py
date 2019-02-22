from django.core.management import BaseCommand
from django.contrib.sites.models import Site
from config import write_config
from constance import config


class Command(BaseCommand):
    help = 'Configures the URL of your website'

    def add_arguments(self, parser):
        parser.add_argument('URL', nargs=1, type=str,
                            help='The URL of your website')

    def handle(self, *args, **options):
        url = options.get('URL')[0]
        name = config.NAME if config.NAME != 'MangAdventure' else url
        write_config('settings', 'site_url', url)
        site = Site.objects.get_or_create(pk=1)[0]
        site.domain = url
        site.name = name
        site.save()
        self.stdout.write(self.style.SUCCESS('Saved URL in config.ini'))


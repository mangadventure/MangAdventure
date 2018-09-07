from django.core.management import BaseCommand
from MangAdventure.utils.random import random_string
from config import write_config


class Command(BaseCommand):
    help = 'Generates a secret key'

    def handle(self, *args, **options):
        message = 'Saved secret key in config.ini'
        write_config('settings', 'secret_key', random_string(50))
        self.stdout.write(self.style.SUCCESS(message))


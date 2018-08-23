from django.core.management import BaseCommand
from random import SystemRandom
from config import write_config


class Command(BaseCommand):
    help = 'Generates a secret key'

    def handle(self, *args, **options):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        rand = ''.join(SystemRandom().choice(chars) for i in range(50))
        write_config('settings', 'secret_key', rand)
        self.stdout.write(self.style.SUCCESS('Saved secret key in config.ini'))




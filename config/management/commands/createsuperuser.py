"""Override the createsuperuser command."""

from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import User


class Command(createsuperuser.Command):
    def handle(self, *args: str, **options: str):
        # HACK: disallow multiple superusers
        if User.objects.filter(is_superuser=True).exists():
            self.stderr.write('A superuser already exists.')
        else:
            super().handle(*args, **options)

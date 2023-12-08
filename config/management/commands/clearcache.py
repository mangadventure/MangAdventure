"""Clear cache command"""

from django.core.cache import cache
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Command used to clear the cache."""
    help = 'Clear the cache.'

    def handle(self, *args: str, **options: str):
        """
        Execute the command.

        :param args: The arguments of the command.
        :param options: The options of the command.
        """
        cache.clear()

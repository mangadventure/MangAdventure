"""Admin logs command"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.admin.models import LogEntry
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

if TYPE_CHECKING:  # pragma: no cover
    from argparse import ArgumentParser


class Command(BaseCommand):
    """Command used to view admin logs."""
    help = 'Outputs admin logs to a file or stdout.'

    def add_arguments(self, parser: ArgumentParser):
        """
        Add arguments to the command.

        :param parser: An ``ArgumentParser`` instance.
        """
        parser.add_argument(
            'file', type=str, nargs='?', default='-',
            help='The file where the logs will be written.'
        )

    def handle(self, *args: str, **options: str):
        """
        Execute the command.

        :param args: The arguments of the command.
        :param options: The options of the command.
        """
        file = options['file']
        out = self.stdout if file == '-' else open(file, 'w')
        try:
            for log in LogEntry.objects.iterator():
                user = log.user.username
                date = log.action_time.isoformat(' ', 'seconds')
                act = log.get_action_flag_display()
                try:
                    obj = repr(log.get_edited_object())
                except ObjectDoesNotExist:
                    obj = '<INACCESSIBLE>'
                msg = f'[{user}] {{{date}}} ({act}) {obj}\n'
                out.write(msg)  # lgtm[py/clear-text-logging-sensitive-data]
        finally:
            if file != '-':
                out.close()

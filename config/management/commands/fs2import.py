"""FoolSlide2 importer."""

from __future__ import annotations

from io import StringIO
from os.path import abspath, join
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

from django.core.files import File
from django.core.management import BaseCommand, CommandError, call_command
from django.db.utils import IntegrityError

from groups.models import Group
from reader.models import Chapter, Page, Series

if TYPE_CHECKING:  # pragma: no cover
    from argparse import ArgumentParser
    from typing import List
    Elem = ET.Element
    Elems = List[ET.Element]


class Command(BaseCommand):
    """Command used to import data from a FoolSlide2 installation."""
    help = 'Imports data from FoolSlide2.'

    def add_arguments(self, parser: ArgumentParser):
        """
        Add arguments to the command.

        :param parser: An ``ArgumentParser`` instance.
        """
        parser.add_argument(
            'root', type=str,
            help='The path to the root directory of the FS2 installation.'
        )
        parser.add_argument(
            'data', type=str,
            help="The path to FS2's exported data (in XML format)."
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_true',
            help='Do NOT prompt the user for input of any kind.'
        )

    def handle(self, *args: str, **options: str):
        """
        Execute the command.

        :param args: The arguments of the command.
        :param options: The options of the command.
        """
        call_command('migrate', stdout=StringIO())  # Set up database
        root = abspath(options['root'])
        data = abspath(options['data'])
        tables = ET.parse(data).findall('database/table')
        content = join(root, 'content', 'comics')
        directories = {'series': [], 'chapters': []}  # type: dict
        elements = {
            'series': self._get_element(tables, 'comics'),
            'chapters': self._get_element(tables, 'chapters'),
            'pages': self._get_element(tables, 'pages'),
            'groups': self._get_element(tables, 'teams')
        }

        if not options['noinput']:  # pragma: no cover
            self._print_warning(
                'Importing FoolSlide2 data requires an empty database.\n'
                'This command will wipe any existing data in the database.\n'
                'Are you sure you want to proceed?\n'
            )
            answer = input("    Type 'yes' to continue, or 'no' to cancel: ")
            if answer.lower() != 'yes':
                self._print('Import cancelled.')
                return
        call_command('flush', '--no-input')

        self._print(f'Importing {self._sql_name("Groups")}...')
        all_groups = []
        for g in elements['groups']:
            group = Group(
                id=self._get_column(g, 'id'),
                name=self._get_column(g, 'name'),
                website=self._get_column(g, 'url'),
                twitter=self._get_column(g, 'twitter'),
                irc=self._get_column(g, 'irc')
            )
            self._print(f'- Found {self._sql_name("Group")}: {group}')
            all_groups.append(group)
        try:
            Group.objects.bulk_create(all_groups)
            self._print_success('Groups successfully imported.')
        except IntegrityError as e:  # pragma: no cover
            raise CommandError('Failed to insert groups') from e

        self._print(f'Importing {self._sql_name("Series")}...')
        all_series = []
        for s in elements['series']:
            slug = self._get_column(s, 'stub')
            series = Series(
                id=self._get_column(s, 'id'), slug=slug,
                title=self._get_column(s, 'name'),
                description=self._get_column(s, 'description'),
            )
            self._print(f'- Found {self._sql_name("Series")}: {series}')
            thumb = self._get_column(s, 'thumbnail')
            series_dir = join(
                content, f'{slug}_{self._get_column(s, "uniqid")}'
            )
            cover = join(series_dir, thumb)
            with open(cover, 'rb') as f:
                series.cover.save(thumb, File(f), save=False)
            all_series.append(series)
            directories['series'].append(
                (self._get_column(s, 'id'), series_dir)
            )
        try:
            Series.objects.bulk_create(all_series)
            self._print_success('Series successfully imported.')
        except IntegrityError as e:  # pragma: no cover
            raise CommandError('Failed to insert series') from e

        self._print(f'Importing {self._sql_name("Chapters")}...')
        all_chapters = []
        chapter_groups = []
        groups_through = Chapter.groups.through
        for c in elements['chapters']:
            cid = self._get_column(c, 'id')
            sid = self._get_column(c, 'comic_id')
            number = float('{chapter}.{subchapter}'.format(
                chapter=self._get_column(c, 'chapter') or '0',
                subchapter=self._get_column(c, 'subchapter') or '0'
            ))
            volume = int(self._get_column(c, 'volume') or '0')
            chapter = Chapter(
                id=cid, series_id=sid,
                title=self._get_column(c, 'name'),
                volume=volume or None, number=number
            )
            self._print(
                f'- Found {self._sql_name("Chapter")}: {chapter.series} '
                f'- {chapter.volume}/{chapter.number:g} - {chapter.title}'
            )
            if gid := self._get_column(c, 'team_id'):
                chapter_groups.append(
                    groups_through(chapter_id=cid, group_id=gid)
                )
            dir_ = next(d[1] for d in directories['series'] if d[0] == sid)
            directories['chapters'].append((
                cid, join(dir_, '{stub}_{uniqid}'.format(
                    stub=self._get_column(c, 'stub'),
                    uniqid=self._get_column(c, 'uniqid')
                ))
            ))
            all_chapters.append(chapter)
        try:
            Chapter.objects.bulk_create(all_chapters)
            groups_through.objects.bulk_create(chapter_groups)  # type: ignore
            self._print_success('Chapters successfully imported.')
        except IntegrityError as e:  # pragma: no cover
            raise CommandError('Failed to insert chapters') from e

        self._print(f'Importing {self._sql_name("Pages")}...')
        all_pages = []
        page_numbers = {}  # type: dict
        for p in self._sort_children(elements['pages'], 'filename'):
            pid = self._get_column(p, 'id')
            cid = self._get_column(p, 'chapter_id')
            page_numbers[cid] = page_numbers.get(cid, 0) + 1
            page = Page(id=pid, chapter_id=cid, number=page_numbers[cid])
            self._print(f'- Found {self._sql_name("Page")}: {page}')
            dir_ = next(d[1] for d in directories['chapters'] if d[0] == cid)
            fname = self._get_column(p, 'filename')
            with open(join(dir_, fname), 'rb') as f:
                page.image.save(fname, File(f), save=False)
            all_pages.append(page)
        try:
            Page.objects.bulk_create(all_pages)
            self._print_success('Chapter pages successfully imported.')
        except IntegrityError as e:  # pragma: no cover
            raise CommandError('Failed to insert pages') from e
        self._print_success('Successfully imported FoolSlide2 data.')

    @staticmethod
    def _get_element(tables: Elems, name: str) -> Elems:
        return list(filter(
            lambda t: t.attrib['name'].endswith(name), tables
        ))

    @staticmethod
    def _get_column(table: Elem, name: str) -> str:
        elem = table.find(f'column[@name="{name}"]')
        return getattr(elem, 'text', None) or ''

    @staticmethod
    def _sort_children(tables: Elems, name: str) -> Elems:
        return sorted(tables, key=lambda p: Command._get_column(p, name))

    def _print(self, text: str, **kwargs):
        self.stdout.write(text, **kwargs)

    def _print_success(self, text: str, **kwargs):
        self._print(self.style.SUCCESS(text), **kwargs)

    def _print_warning(self, text: str, **kwargs):  # pragma: no cover
        self._print(self.style.WARNING(text), **kwargs)

    def _sql_name(self, name: str) -> str:
        return self.style.SQL_TABLE(name)


__all__ = ['Command']

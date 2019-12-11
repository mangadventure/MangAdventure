"""FoolSlide2 importer."""

from os.path import abspath, join
from typing import TYPE_CHECKING
from xml.etree import cElementTree as et

from django.core.files import File
from django.core.management import BaseCommand

from groups.models import Group
from reader.models import Chapter, Page, Series

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from typing import List
    Elem = et.Element
    Tree = et.ElementTree
    Trees = List[et.ElementTree]


class Command(BaseCommand):
    """Command used to import data from a FoolSlide2 installation."""
    help = 'Imports data from FoolSlide2.'

    def add_arguments(self, parser: 'ArgumentParser'):
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

    def handle(self, *args: str, **options: str):
        """
        Execute the command.

        :param args: The arguments of the command.
        :param options: The options of the command.
        """
        root = abspath(options['root'])
        data = abspath(options['data'])
        tables = et.parse(data).findall('database/table')
        content = join(root, 'content', 'comics')
        directories = {'series': [], 'chapters': []}
        elements = {
            'series': self._get_element(tables, 'comics'),
            'chapters': self._get_element(tables, 'chapters'),
            'pages': self._get_element(tables, 'pages'),
            'groups': self._get_element(tables, 'teams')
        }

        all_groups = []
        for g in elements['groups']:
            group = Group(
                id=self._get_column(g, 'id'),
                name=self._get_column(g, 'name'),
                website=self._get_column(g, 'url'),
                twitter=self._get_column(g, 'twitter'),
                irc=self._get_column(g, 'irc')
            )
            all_groups.append(group)
        Group.objects.bulk_create(all_groups)

        all_series = []
        for s in elements['series']:
            slug = self._get_column(s, 'stub')
            series = Series(
                id=self._get_column(s, 'id'), slug=slug,
                title=self._get_column(s, 'name'),
                description=self._get_column(s, 'description'),
            )
            thumb = self._get_column(s, 'thumbnail')
            series_dir = join(content, '{slug}_{uniqid}'.format(
                slug=slug, uniqid=self._get_column(s, 'uniqid')
            ))
            cover = join(series_dir, f'thumb_{thumb}')
            with open(cover, 'rb') as f:
                series.cover.save(thumb, File(f), save=False)
            all_series.append(series)
            directories['series'].append(
                (self._get_column(s, 'id'), series_dir)
            )
        Series.objects.bulk_create(all_series)

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
                volume=volume, number=number
            )
            gid = self._get_column(c, 'team_id')
            if gid:
                chapter_groups.append(
                    groups_through(chapter_id=cid, group_id=gid)
                )
            _dir = next(d[1] for d in directories['series'] if d[0] == sid)
            directories['chapters'].append((
                cid, join(_dir, '{stub}_{uniqid}'.format(
                    stub=self._get_column(c, 'stub'),
                    uniqid=self._get_column(c, 'uniqid')
                ))
            ))
            all_chapters.append(chapter)
        Chapter.objects.bulk_create(all_chapters)
        groups_through.objects.bulk_create(chapter_groups)

        all_pages = []
        page_numbers = {}
        for p in self._sort_children(elements['pages'], 'filename'):
            pid = self._get_column(p, 'id')
            cid = self._get_column(p, 'chapter_id')
            page_numbers[cid] = page_numbers.get(cid, 0) + 1
            page = Page(id=pid, chapter_id=cid, number=page_numbers[cid])
            _dir = next(d[1] for d in directories['chapters'] if d[0] == cid)
            fname = self._get_column(p, 'filename')
            with open(join(_dir, fname), 'rb') as f:
                page.image.save(fname, File(f), save=False)
            all_pages.append(page)
        Page.objects.bulk_create(all_pages)

        @staticmethod
        def _get_element(tables: 'Tree', name: str) -> 'Trees':
            return list(filter(
                lambda t: t.attrib['name'].endswith(name), tables
            ))

        @staticmethod
        def _get_column(table: 'Elem', name: str) -> str:
            text = table.find(f'column[@name="{name}"]').text
            return text if text is not None else ''

        @staticmethod
        def _sort_children(tables: 'Tree', name: str) -> 'Trees':
            return sorted(tables, key=lambda p: _get_column(p, name))


__all__ = ['Command']

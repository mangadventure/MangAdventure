from os.path import abspath, join
from xml.etree import cElementTree as et

from django.core.files import File
from django.core.management import BaseCommand

from groups.models import Group
from reader.models import Chapter, Page, Series


def _get_element(tables, name):
    return list(filter(
        lambda t: t.attrib['name'].endswith(name), tables
    ))


def _get_column(table, name):
    text = table.find(f'column[@name="{name}"]').text
    return text if text is not None else ''


def _sort_children(tables, name):
    return sorted(tables, key=lambda p: _get_column(p, name))


class Command(BaseCommand):
    help = 'Imports data from FoolSlide2.'

    def add_arguments(self, parser):
        parser.add_argument(
            'root', type=str,
            help='The path to the root directory of the FS2 installation.'
        )
        parser.add_argument(
            'data', type=str,
            help="The path to FS2's exported data (in XML format)."
        )

    def handle(self, *args, **options):
        root = abspath(options['root'])
        data = abspath(options['data'])
        tables = et.parse(data).findall('database/table')
        content = join(root, 'content', 'comics')
        directories = {'series': [], 'chapters': []}
        elements = {
            'series': _get_element(tables, 'comics'),
            'chapters': _get_element(tables, 'chapters'),
            'pages': _get_element(tables, 'pages'),
            'groups': _get_element(tables, 'teams')
        }

        all_groups = []
        for g in elements['groups']:
            group = Group(
                id=_get_column(g, 'id'),
                name=_get_column(g, 'name'),
                website=_get_column(g, 'url'),
                twitter=_get_column(g, 'twitter'),
                irc=_get_column(g, 'irc')
            )
            all_groups.append(group)
        Group.objects.bulk_create(all_groups)

        all_series = []
        for s in elements['series']:
            slug = _get_column(s, 'stub')
            series = Series(
                id=_get_column(s, 'id'), slug=slug,
                title=_get_column(s, 'name'),
                description=_get_column(s, 'description'),
            )
            thumb = _get_column(s, 'thumbnail')
            series_dir = join(content, '{slug}_{uniqid}'.format(
                slug=slug, uniqid=_get_column(s, 'uniqid')
            ))
            cover = join(series_dir, 'thumb_%s' % thumb)
            with open(cover, 'rb') as f:
                series.cover.save(thumb, File(f), save=False)
            all_series.append(series)
            directories['series'].append(
                (_get_column(s, 'id'), series_dir)
            )
        Series.objects.bulk_create(all_series)

        all_chapters = []
        chapter_groups = []
        groups_through = Chapter.groups.through
        for c in elements['chapters']:
            cid = _get_column(c, 'id')
            sid = _get_column(c, 'comic_id')
            number = float('{chapter}.{subchapter}'.format(
                chapter=_get_column(c, 'chapter') or '0',
                subchapter=_get_column(c, 'subchapter') or '0'
            ))
            volume = int(_get_column(c, 'volume') or '0')
            chapter = Chapter(
                id=cid, series_id=sid,
                title=_get_column(c, 'name'),
                volume=volume, number=number
            )
            gid = _get_column(c, 'team_id')
            if gid:
                chapter_groups.append(
                    groups_through(chapter_id=cid, group_id=gid)
                )
            _dir = next(d[1] for d in directories['series'] if d[0] == sid)
            directories['chapters'].append((
                cid, join(_dir, '{stub}_{uniqid}'.format(
                    stub=_get_column(c, 'stub'),
                    uniqid=_get_column(c, 'uniqid')
                ))
            ))
            all_chapters.append(chapter)
        Chapter.objects.bulk_create(all_chapters)
        groups_through.objects.bulk_create(chapter_groups)

        all_pages = []
        page_numbers = {}
        for p in _sort_children(elements['pages'], 'filename'):
            pid = _get_column(p, 'id')
            cid = _get_column(p, 'chapter_id')
            page_numbers[cid] = page_numbers.get(cid, 0) + 1
            page = Page(id=pid, chapter_id=cid, number=page_numbers[cid])
            _dir = next(d[1] for d in directories['chapters'] if d[0] == cid)
            fname = _get_column(p, 'filename')
            with open(join(_dir, fname), 'rb') as f:
                page.image.save(fname, File(f), save=False)
            all_pages.append(page)
        Page.objects.bulk_create(all_pages)

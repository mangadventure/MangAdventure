from unittest.mock import patch

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.core.cache import cache
from django.db.models.fields.files import ImageFileDescriptor

from MangAdventure.tests.utils import get_test_image, get_valid_zip_file

from reader.models import Series

from . import ReaderTestBase


def get_redirect_list() -> list[tuple[str, str]]:
    return list(Redirect.objects.values_list('old_path', 'new_path'))


class TestRedirectSeries(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.create(
            title='Old Slug', slug='old-slug', cover=get_test_image()
        )
        self.chapter = self.series.chapters.create(
            title='Chapter', number=1, file=get_valid_zip_file()
        )

    def test_slug(self):
        self.series.title = 'New Slug'
        self.series.save(update_fields=('title', 'slug'))
        assert self.series.slug == 'new-slug'

    def test_redirect(self):
        url1 = self.series.get_absolute_url()

        self.series.slug = 'new-slug'
        self.series.save(update_fields=('slug',))
        url2 = self.series.get_absolute_url()
        assert get_redirect_list() == [(url1, url2)]

        self.series.slug = 'another-slug'
        self.series.save(update_fields=('slug',))
        url3 = self.series.get_absolute_url()
        assert get_redirect_list() == [(url2, url3), (url1, url3)]

        for name in ('new-slug', 'old-slug'):
            assert name not in self.series.cover.name
            assert name not in self.chapter.pages.first().image.name

        self.series.slug = 'old-slug'
        self.series.save(update_fields=('slug',))
        assert get_redirect_list() == [(url3, url1), (url2, url1)]


class TestRedirectChapter(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.create(
            title='series', slug='old-slug', cover=get_test_image()
        )
        self.chapter = self.series.chapters.create(
            title='Chapter', number=1, file=get_valid_zip_file()
        )

    @patch.object(
        ImageFileDescriptor, '__set__',
        ImageFileDescriptor.__mro__[1].__set__)  # type: ignore
    def test_redirect(self):
        self.chapter.number = 2
        self.chapter.volume = 2
        self.chapter.save(update_fields=('number', 'volume'))
        series_path = settings.MEDIA_ROOT / self.series.get_directory()
        assert (series_path / '2' / '2').exists()
        assert not (series_path / '0' / '1').exists()


class TestCompleteSeries(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.create(
            title='series', slug='old-slug', cover=get_test_image()
        )

    def test_complete(self):
        assert self.series.status == 'ongoing'
        self.series.chapters.create(
            title='Chapter', number=1, final=True, file=get_valid_zip_file()
        )
        assert self.series.status == 'completed'


class TestClearChapterCache(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.create(title='series')

    def test_save(self):
        cache.set(f'reader.chapters.{self.series.slug}', [])
        self.series.chapters.create(title='Chapter', number=1)
        assert f'reader.chapters.{self.series.slug}' not in cache

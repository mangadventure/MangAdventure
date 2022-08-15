from typing import List, Tuple

from django.conf import settings
from django.contrib.redirects.models import Redirect

from MangAdventure.tests.utils import get_test_image, get_valid_zip_file

from reader.models import Series

from . import ReaderTestBase


def get_redirect_list() -> List[Tuple[str, str]]:
    redirects = Redirect.objects.values_list('old_path', 'new_path')
    return list(redirects)  # type: ignore


class TestRedirectSeries(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.create(
            title='series', slug='old-slug', cover=get_test_image()
        )
        self.chapter = self.series.chapters.create(
            title='Chapter', number=1, file=get_valid_zip_file()
        )

    def test_redirect(self):
        url1 = self.series.get_absolute_url()

        self.series.slug = 'new-slug'
        self.series.save()
        url2 = self.series.get_absolute_url()
        assert get_redirect_list() == [(url1, url2)]

        self.series.slug = 'another-slug'
        self.series.save()
        url3 = self.series.get_absolute_url()
        assert get_redirect_list() == [(url2, url3), (url1, url3)]

        for name in ('new-slug', 'old-slug'):
            assert name not in self.series.cover.name
            assert name not in self.chapter.pages.first().image.name

        self.series.slug = 'old-slug'
        self.series.save()
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

    def test_redirect(self):
        self.chapter.number = 2
        self.chapter.volume = 2
        self.chapter.save()
        series_path = settings.MEDIA_ROOT / self.series.get_directory()
        assert (series_path / '2' / '2').exists()
        assert not (series_path / '0' / '1').exists()


class TestRemovePage(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        series = Series.objects.create(title='series')
        chapter = series.chapters.create(title='Chapter', number=1)
        self.page = chapter.pages.create(number=1, image=get_test_image())

    def test_delete(self):
        from os.path import exists
        path = self.page.image.path
        assert exists(path)
        self.page.delete()
        assert not exists(path)

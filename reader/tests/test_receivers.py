from pathlib import Path
from typing import TYPE_CHECKING, Tuple

from django.conf import settings
from django.contrib.redirects.models import Redirect

from MangAdventure.tests import get_test_image, get_valid_zip_file

from reader.models import Series

from . import ReaderTestBase

if TYPE_CHECKING:
    from reader.models import Chapter  # noqa


def get_redirect_list() -> list:
    return list(Redirect.objects.values_list('old_path', 'new_path'))


class TestRedirectSeries(ReaderTestBase):
    @staticmethod
    def setup_series() -> Tuple['Series', 'Chapter']:
        series = Series.objects.create(title='series', slug='old-slug',
                                       cover=get_test_image())
        chapter = series.chapters.create(title='Chapter', number=1,
                                         file=get_valid_zip_file())
        return series, chapter

    def test_redirect(self):
        series = self.setup_series()[0]

        url1 = series.get_absolute_url()

        series.slug = 'new-slug'
        series.save()
        url2 = series.get_absolute_url()
        assert get_redirect_list() == [(url1, url2)]

        series.slug = 'another-slug'
        series.save()
        url3 = series.get_absolute_url()
        assert get_redirect_list() == [(url2, url3), (url1, url3)]

        for name in ['new-slug', 'old-slug']:
            assert name not in series.cover.name
            assert name not in series.chapters.first().pages.first().image.name

        series.slug = 'old-slug'
        series.save()
        assert get_redirect_list() == [(url3, url1), (url2, url1)]


class TestRedirectChapter(ReaderTestBase):
    def test_redirect(self):
        series, chapter = TestRedirectSeries.setup_series()
        chapter.number = 2
        chapter.volume = 2
        chapter.save()
        series_path = Path(settings.MEDIA_ROOT) / series.get_directory()
        assert (series_path / '2' / '2').exists()
        assert not (series_path / '0' / '1').exists()

from MangAdventure.tests.utils import get_test_image

from reader.models import Chapter, Series
from reader.sitemaps import ChapterSitemap, SeriesSitemap

from . import ReaderTestBase


class TestSitemaps(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series1 = Series.objects.create(
            title='Series1', cover=get_test_image()
        )
        self.chapter1 = Chapter.objects.create(
            title='Chapter1', number=1.0, series=self.series1
        )
        self.series2 = Series.objects.create(title='Series2')
        self.chapter2 = Chapter.objects.create(
            title='Chapter2', number=1.0, series=self.series2
        )

    def test_series(self):
        sitemap = SeriesSitemap()
        assert list(sitemap.items()) == [self.series1, self.series2]
        assert sitemap.lastmod(self.series2) == self.series2.modified
        assert self.series1.sitemap_images == [self.series1.cover.url]

    def test_chapters(self):
        sitemap = ChapterSitemap()
        assert list(sitemap.items()) == [self.chapter1, self.chapter2]
        assert sitemap.lastmod(self.chapter1) == self.chapter1.modified
        assert self.chapter2.sitemap_images == []

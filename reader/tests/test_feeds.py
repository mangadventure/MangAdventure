from django.http import HttpRequest
from django.utils.feedgenerator import Atom1Feed

from MangAdventure.tests.utils import get_test_image

from reader.feeds import LibraryAtom, LibraryRSS, ReleasesAtom, ReleasesRSS
from reader.models import Chapter, Series

from . import ReaderTestBase


class FeedsTestBase(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.request = HttpRequest()
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
        self.series2.categories.create(name='Category')


class TestLibrary(FeedsTestBase):
    def _test_feed(self, feed, series):
        assert feed.link == '/reader/'
        assert feed.author_name == 'MangAdventure'
        assert feed.title == 'Library - MangAdventure'
        if feed.feed_type is Atom1Feed:
            assert feed.subtitle == 'Updates when a new series is added'
        else:
            assert feed.description == 'Updates when a new series is added'
        assert list(feed.items()) == [self.series2, self.series1]
        assert feed.item_title(series) == str(series)
        assert feed.item_pubdate(series) == series.created
        assert feed.item_updateddate(series) == series.modified

    def test_atom(self):
        feed = LibraryAtom()
        self._test_feed(feed, self.series1)
        r = feed(self.request)
        date = self.series1.modified.isoformat()
        assert f'<updated>{date}' in str(r.content)
        assert self.series1.cover.name in str(r.content)

    def test_rss(self):
        feed = LibraryRSS()
        self._test_feed(feed, self.series2)
        r = feed(self.request)
        assert '<category>Category' in str(r.content)
        assert '<guid isPermaLink="true"' in str(r.content)
        assert '<enclosure>' not in str(r.content)


class TestReleases(FeedsTestBase):
    def _test_feed(self, feed, chapter):
        assert feed.author_name == 'MangAdventure'
        assert feed.item_title(chapter) == str(chapter)
        assert feed.item_pubdate(chapter) == chapter.uploaded
        assert feed.item_updateddate(chapter) == chapter.modified

    def test_atom_all(self):
        feed = ReleasesAtom()
        assert feed.link(None) == '/'
        assert feed.title(None) == 'Releases - MangAdventure'
        assert feed.subtitle(None) == 'Updates when a new chapter is added'
        assert list(feed.items(None)) == [self.chapter2, self.chapter1]
        self._test_feed(feed, self.chapter1)
        r = feed(self.request)
        date = self.chapter1.modified.isoformat()
        assert f'<updated>{date}' in str(r.content)

    def test_rss_all(self):
        feed = ReleasesRSS()
        self._test_feed(feed, self.chapter2)
        obj = feed.get_object(self.request)
        assert feed.link(obj) == '/'
        assert feed.title(obj) == 'Releases - MangAdventure'
        assert feed.description(obj) == 'Updates when a new chapter is added'
        assert list(feed.items(obj)) == [self.chapter2, self.chapter1]
        r = feed(self.request)
        assert '<guid isPermaLink="true"' in str(r.content)

    def test_atom_series(self):
        feed = ReleasesAtom()
        assert feed.link(self.series1) == self.series1.get_absolute_url()
        assert feed.title(self.series1) == 'Series1 - MangAdventure'
        assert feed.subtitle(self.series1) == \
            'Updates when a new chapter of Series1 is added'
        assert list(feed.items(self.series1)) == [self.chapter1]
        self._test_feed(feed, self.chapter1)
        r = feed(self.request, self.series1.slug)
        date = self.chapter1.modified.isoformat()
        assert f'<updated>{date}' in str(r.content)

    def test_rss_series(self):
        feed = ReleasesRSS()
        obj = feed.get_object(self.request, self.series2.slug)
        assert feed.link(obj) == self.series2.get_absolute_url()
        assert feed.title(obj) == 'Series2 - MangAdventure'
        assert feed.description(obj) == \
            'Updates when a new chapter of Series2 is added'
        assert list(feed.items(obj)) == [self.chapter2]
        self._test_feed(feed, self.chapter2)
        r = feed(self.request, self.series2.slug)
        assert '<guid isPermaLink="true"' in str(r.content)

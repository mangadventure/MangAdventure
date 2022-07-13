from operator import attrgetter
from typing import Dict, List

from django.core.cache import cache
from django.urls import reverse

from pytest import importorskip

from MangAdventure.utils import natsort

from reader.models import Series

from .base import MangadvTestBase
from .utils import get_test_image, get_valid_zip_file


class MangadvViewTestBase(MangadvTestBase):
    def setup_method(self):
        super().setup_method()
        series = Series.objects.create(title='series', cover=get_test_image())
        series.aliases.create(name='first series')
        author = series.authors.create(name='Author')
        author.aliases.create(name='author1')
        artist = series.artists.create(name='Artist')
        artist.aliases.create(name='artist1')
        series.categories.create(name='Manga')
        category = series.categories.create(name='Adventure')
        series.chapters.create(
            title='chapter', number=1, file=get_valid_zip_file()
        )

        series2 = Series.objects.create(title='series2', completed=True)
        author2 = series2.authors.create(name='Author 2')
        author2.aliases.create(name='author2')
        artist2 = series2.artists.create(name='Artist 2')
        artist2.aliases.create(name='artist2')
        series2.chapters.create(title='chapter', number=1, final=True)
        series2.categories.create(name='Yaoi')
        series2.categories.add(category)

    def teardown_method(self):
        super().teardown_method()
        cache.clear()


class TestIndex(MangadvViewTestBase):
    URL = reverse('index')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200

    def test_csp(self):
        importorskip('csp', reason='requires django-csp')
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert 'Content-Security-Policy' in r
        assert 'unsafe-inline' not in r['Content-Security-Policy']


class TestSearch(MangadvViewTestBase):
    URL = reverse('search')

    def _test_filter(self, params: Dict[str, str] = {},
                     results: List[str] = []):
        cache.clear()
        r = self.client.get(self.URL, params)
        assert r.status_code == 200
        if bool(params and results):
            values = map(attrgetter('title'), r.context['results'])
            assert natsort(values) == results

    def test_get_simple(self):
        self._test_filter()

    def test_get_query(self):
        self._test_filter({'q': 'first'}, ['series'])

    def test_get_author(self):
        self._test_filter({'author': 'author1'}, ['series'])
        self._test_filter({'author': 'artist1'}, ['series'])
        self._test_filter({'author': 'author2'}, ['series2'])
        self._test_filter({'author': 'artist2'}, ['series2'])

    def test_get_status(self):
        self._test_filter({'status': 'any'}, [])
        self._test_filter({'status': 'completed'}, ['series2'])
        self._test_filter({'status': 'ongoing'}, ['series'])
        self._test_filter({'status': 'any', 'q': 's'}, ['series', 'series2'])

    def test_get_categories(self):
        self._test_filter({'categories': 'adventure'}, ['series', 'series2'])
        self._test_filter({'categories': 'manga'}, ['series'])
        self._test_filter({'categories': 'yaoi'}, ['series2'])
        self._test_filter({'categories': '-yaoi,adventure'}, ['series'])


class TestOpenSearch(MangadvViewTestBase):
    URL = reverse('opensearch')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert r['Content-Type'] == 'application/opesearchdescription+xml'
        assert '<ShortName>MangAdventure' in str(r.content)


class TestContribute(MangadvViewTestBase):
    URL = reverse('contribute')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert r['Content-Type'] == 'application/json'
        assert r.json()['name'] == 'MangAdventure'


class TestManifest(MangadvViewTestBase):
    URL = reverse('manifest')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert r['Content-Type'] == 'application/manifest+json'
        assert r.json()['name'] == 'MangAdventure'

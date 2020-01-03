from django.core.cache import cache
from django.urls import reverse

from reader.models import Series

from . import MangadvTestBase, get_test_image, get_valid_zip_file


class MangadvViewTestBase(MangadvTestBase):
    @staticmethod
    def setup_chapters():
        series = Series.objects.create(title='series', cover=get_test_image())
        series.aliases.create(alias='first series')
        author = series.authors.create(name='Author')
        author.aliases.create(alias='author1')
        artist = series.artists.create(name='Artist')
        artist.aliases.create(alias='artist1')
        series.categories.create(name='Manga')
        category = series.categories.create(name='Adventure')
        series.chapters.create(title='chapter', number=1,
                               file=get_valid_zip_file())

        series2 = Series.objects.create(title='series2', completed=True)
        author2 = series2.authors.create(name='Author 2')
        author2.aliases.create(alias='author2')
        artist2 = series2.artists.create(name='Artist 2')
        artist2.aliases.create(alias='artist2')
        series2.chapters.create(title='chapter', number=1, final=True)
        series2.categories.create(name='Yaoi')
        series2.categories.add(category)

    def teardown_method(self):
        super().teardown_method()
        cache.clear()


class TestIndex(MangadvViewTestBase):
    URL = reverse('index')

    def test_get(self):
        self.setup_chapters()
        r = self.client.get(self.URL)
        assert r.status_code == 200


class TestSearch(MangadvViewTestBase):
    URL = reverse('search')

    def _test_filter(self, _filter: dict = {}, results: list = [], empty=False):
        cache.clear()
        r = self.client.get(self.URL, _filter)
        assert r.status_code == 200
        if not empty:
            assert list(r.context['results'].values_list('title',
                                                         flat=True)) == results

    def test_get_simple(self):
        self.setup_chapters()
        self._test_filter(empty=True)

    def test_get_author_search_alias(self):
        self.setup_chapters()
        self._test_filter({'author': 'author1'}, ['series'])
        self._test_filter({'author': 'artist1'}, ['series'])
        self._test_filter({'author': 'author2'}, ['series2'])
        self._test_filter({'author': 'artist2'}, ['series2'])

    def test_get_completed(self):
        self.setup_chapters()
        self._test_filter({'status': 'completed'}, ['series2'])
        self._test_filter({'status': 'any'}, ['series', 'series2'])

    def test_get_categories(self):
        self.setup_chapters()
        self._test_filter({'categories': 'adventure'}, ['series', 'series2'])
        self._test_filter({'categories': 'manga'}, ['series'])
        self._test_filter({'categories': 'yaoi'}, ['series2'])
        self._test_filter({'categories': '-yaoi,adventure'}, ['series'])

    def test_get_query(self):
        self.setup_chapters()
        self._test_filter({'q': 'first'}, ['series'])


class TestOpensearch(MangadvViewTestBase):
    URL = reverse('opensearch')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert r['content-type'] == 'application/opesearchdescription+xml'


class TestContribute(MangadvViewTestBase):
    URL = reverse('contribute')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert r['content-type'] == 'application/json'

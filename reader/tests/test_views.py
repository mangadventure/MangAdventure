from django.core.cache import cache
from django.http import FileResponse
from django.urls import reverse

from pytest import mark

from MangAdventure.tests.utils import get_test_image, get_valid_zip_file

from reader.models import Series

from . import ReaderTestBase


class ReaderViewTestBase(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.create(
            title='series', cover=get_test_image()
        )
        self.series.chapters.create(
            title='chapter', file=get_valid_zip_file(), number=1
        )

    def teardown_method(self):
        super().teardown_method()
        cache.clear()


class TestDirectory(ReaderViewTestBase):
    URL = reverse('reader:directory')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200


class TestSeries(ReaderViewTestBase):
    def test_get(self):
        url = reverse('reader:series', kwargs={'slug': 'series'})
        r = self.client.get(url)
        assert r.status_code == 200

    def test_get_not_found(self):
        url = reverse('reader:series', kwargs={'slug': 'not-found'})
        r = self.client.get(url)
        assert r.status_code == 404

    def test_get_unavailable(self):
        self.series.chapters.all().delete()
        self.client.logout()
        url = reverse('reader:series', kwargs={'slug': 'series'})
        r = self.client.get(url)
        assert r.status_code == 403


class TestChapterPage(ReaderViewTestBase):
    _values = [('series', 0), ('series', 3), ('series2', 1)]

    def test_get(self):
        url = reverse('reader:page', kwargs={
            'slug': 'series', 'vol': 0, 'num': 1, 'page': 1
        })
        r = self.client.get(url)
        assert r.status_code == 200

    @mark.parametrize('values', _values)
    def test_get_not_found(self, values):
        url = reverse('reader:page', kwargs={
            'slug': values[0], 'vol': 1, 'num': 1, 'page': values[1]
        })
        r = self.client.get(url)
        assert r.status_code == 404


class TestChapterRedirect(ReaderViewTestBase):
    def test_get(self):
        url = reverse('reader:chapter', kwargs={
            'slug': 'series', 'vol': 0, 'num': 1
        })
        page_url = reverse('reader:page', kwargs={
            'slug': 'series', 'vol': 0, 'num': 1, 'page': 1
        })
        r1 = self.client.get(url, follow=True)
        assert r1.status_code == 200

        r2 = self.client.get(page_url)
        assert r2.status_code == 200

        assert str(r1.content) == str(r2.content)

    def test_no_match(self):
        r = self.client.get('/reader/series/0/6936167464014960228/')
        assert r.status_code == 404


class TestChapterDownload(ReaderViewTestBase):
    def test_get(self):
        url = reverse('reader:cbz', kwargs={
            'slug': 'series', 'vol': 0, 'num': 1
        })
        self.client.force_login(self.user)
        r = self.client.get(url)
        assert r.status_code == 200
        assert isinstance(r, FileResponse)
        assert r.filename.endswith('c1.cbz')

    def test_get_not_found(self):
        self.series.chapters.all().delete()
        url = reverse('reader:cbz', kwargs={
            'slug': 'series', 'vol': 0, 'num': 1
        })
        self.client.force_login(self.user)
        r = self.client.get(url)
        assert r.status_code == 404

    def test_get_unauthorized(self):
        url = reverse('reader:cbz', kwargs={
            'slug': 'series', 'vol': 0, 'num': 1
        })
        self.client.logout()
        r = self.client.get(url)
        assert r.status_code == 401

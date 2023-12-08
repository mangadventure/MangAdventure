from django.conf import settings

from pytest import mark

from MangAdventure.storage import (
    CDNStorage, ProcessedStaticFilesFinder, ProcessedStaticFilesStorage
)
from MangAdventure.tests.base import MangadvTestBase


@mark.parametrize('name', ('COMPILED/style.css', 'styles/noscript.css'))
def test_static_finder(name):
    finder = ProcessedStaticFilesFinder()
    root = settings.STATIC_ROOT
    location = finder.find_location(str(root / 'styles'), name, 'styles')
    assert location == str(root / name)


class TestStaticStorage(MangadvTestBase):
    def setup_method(self):
        super().setup_method()
        self.storage = ProcessedStaticFilesStorage()

    def test_unprocessed_url(self):
        url = self.storage.url('styles/noscript.css')
        assert url == '/static/styles/noscript.css'

    def test_processed_url(self):
        url = self.storage.url('styles/style.scss')
        assert url == '/static/COMPILED/style.css'

    def test_post_process(self):
        files = self.storage.post_process({
            'styles/style.scss': (self.storage, 'style.scss'),
            'styles/noscript.css': (self.storage, 'noscript.css')
        })
        assert next(files)[1].endswith('/COMPILED/style.css')
        assert next(files)[1].rsplit('/', 1)[-1] == 'noscript.css'


class TestCDNStorage(MangadvTestBase):
    _cdns = {
        'statically': 'https://cdn.statically.io',
        'weserv': 'https://images.weserv.nl',
        'photon': 'https://i3.wp.com'
    }

    def setup_method(self):
        super().setup_method()
        self.storage = CDNStorage((300, 300))

    @mark.parametrize('name', _cdns.keys())
    def test_cdn_url(self, name):
        self.storage._cdn = name
        url = self.storage.url('test.jpeg')
        assert url.startswith(self._cdns[name])

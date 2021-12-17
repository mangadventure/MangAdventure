from pytest import mark

from MangAdventure.storage import CDNStorage
from MangAdventure.tests.base import MangadvTestBase


class TestStorage(MangadvTestBase):
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

from pytest import mark

from MangAdventure.sitemaps import MiscSitemap
from MangAdventure.tests.base import MangadvTestBase


class TestSitemaps(MangadvTestBase):
    _pages = {
        'index': ('/', 0.8, 'daily'),
        'search': ('/search/', 0.5, 'never'),
        'reader:directory': ('/reader/', 0.8, 'daily'),
        'info': ('/info/', 0.5, 'never'),
        'privacy': ('/privacy/', 0.5, 'never')
    }

    def setup_method(self):
        super().setup_method()
        self.sitemap = MiscSitemap()

    def test_items(self):
        assert list(self.sitemap.items()) == list(self._pages.keys())

    @mark.parametrize('page', _pages.keys())
    def test_page(self, page):
        assert self.sitemap.location(page) == self._pages[page][0]
        assert self.sitemap.priority(page) == self._pages[page][1]
        assert self.sitemap.changefreq(page) == self._pages[page][2]

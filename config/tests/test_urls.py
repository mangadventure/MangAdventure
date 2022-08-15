from django.urls import reverse

from pytest import importorskip

from . import ConfigTestBase


class TestInfoPage(ConfigTestBase):
    URL = reverse('info')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert '<title>About us' in str(r.content)

    def test_csp(self):
        importorskip('csp', reason='requires django-csp')
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert 'Content-Security-Policy' in r
        assert 'unsafe-inline' in r['Content-Security-Policy']

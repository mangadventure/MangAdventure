from importlib.util import find_spec

from django.shortcuts import reverse

from pytest import mark

from . import ConfigTestBase


class TestInfoPage(ConfigTestBase):
    URL = reverse('info')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert '<title>About us' in str(r.content)

    @mark.skipif(not find_spec('csp'), reason='requires django-csp')
    def test_csp(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        assert 'Content-Security-Policy' in r
        assert 'unsafe-inline' in r['Content-Security-Policy']

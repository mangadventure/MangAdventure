import warnings

from django.core.cache import cache
from django.urls import reverse

from pytest import mark

from . import APITestBase

# TODO: write the rest of the tests
warnings.formatwarning = lambda m, *_: m + '\n'
warnings.warn('API v2 tests are incomplete')


class APIViewTestBase(APITestBase):
    def teardown_method(self):
        super().teardown_method()
        cache.clear()


class TestOpenAPI(APIViewTestBase):
    _redirects = {
        'swagger': 'https://generator.swagger.io',
        'redoc': 'https://redocly.github.io'
    }

    def test_schema(self):
        r = self.client.get(reverse('api:v2:schema'))
        assert r.status_code == 200
        assert r.json()['info']['title'] == 'MangAdventure API'

    @mark.parametrize('name', _redirects.keys())
    def test_redirect(self, name):
        r = self.client.get(reverse(f'api:v2:{name}'))
        assert r.status_code == 301
        assert r['Location'].startswith(self._redirects[name])

import warnings
from datetime import datetime

from django.core.cache import cache
from django.urls import reverse

from MangAdventure.storage import CDNStorage

from . import APITestBase

# TODO: write the rest of the tests
warnings.formatwarning = lambda m, *_: m + '\n'
warnings.warn('API v2 tests are incomplete')


class APIViewTestBase(APITestBase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        # TODO: figure out how to do this properly with mock
        CDNStorage._original_get_modified_time = CDNStorage.get_modified_time
        CDNStorage.get_modified_time = lambda *_: datetime.now()

    def teardown_method(self):
        super().teardown_method()
        cache.clear()

    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        CDNStorage.get_modified_time = CDNStorage._original_get_modified_time
        del CDNStorage._original_get_modified_time


class TestOpenAPI(APIViewTestBase):
    def test_schema(self):
        r = self.client.get(reverse('api:v2:schema'))
        assert r.status_code == 200
        assert r.json()['info']['title'] == 'MangAdventure API'

    def test_swagger(self):
        r = self.client.get(reverse('api:v2:swagger'))
        assert r.status_code == 301
        assert 'generator.swagger.io' in r['Location']

    def test_redoc(self):
        r = self.client.get(reverse('api:v2:redoc'))
        assert r.status_code == 301
        assert 'redocly.github.io' in r['Location']

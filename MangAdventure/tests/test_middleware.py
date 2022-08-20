from random import randint

from django.conf import settings
from django.test import Client
from django.urls import reverse

from pytest import mark

from MangAdventure.bad_bots import BOTS

from .base import MangadvTestBase


class TestBaseMiddleware(MangadvTestBase):
    def setup_method(self):
        super().setup_method()
        bot = BOTS[randint(0, len(BOTS) - 1)]
        self.bot = Client(HTTP_USER_AGENT=bot)

    def test_robots(self):
        r = self.bot.get(reverse('robots'))
        assert r.status_code == 200
        r = self.bot.get(reverse('index'))
        assert r.status_code == 403

    def test_early_data(self):
        r = self.client.get(reverse('index'), HTTP_EARLY_DATA='1')
        assert r.status_code == 425


@mark.skipif(
    settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL != 'https',
    reason='PreloadMiddleware requires HTTPS'
)
class TestPreloadMiddleware(MangadvTestBase):
    def test_preload(self):
        r = self.client.get(reverse('index'))
        assert 'style.css>; as=style' in r['Link']
        r = self.client.get(reverse('opensearch'))
        assert 'Link' not in r

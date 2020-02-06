from os import getenv
from random import randint

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


@mark.skipif(
    getenv('wsgi.url_scheme') != 'https',
    reason='PreloadMiddleware requires HTTPS'
)
class TestPreloadMiddleware(MangadvTestBase):
    def setup_method(self):
        super().setup_method()

    def test_preload(self):
        r = self.client.get(reverse('index'))
        assert 'style.css>; as=style' in r['Link']
        r = self.client.get(reverse('opensearch'))
        assert 'Link' not in r

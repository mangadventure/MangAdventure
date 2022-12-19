from random import randint

from django.test import Client
from django.urls import reverse

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

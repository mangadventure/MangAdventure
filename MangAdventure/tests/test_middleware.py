from random import randint

from django.test import Client
from django.urls import reverse

from MangAdventure.bad_bots import BOTS

from . import MangadvTestBase


class TestBaseMiddleware(MangadvTestBase):
    def setup_method(self):
        bot = BOTS[randint(0, len(BOTS) - 1)]
        self.client = Client(HTTP_USER_AGENT=bot)

    def test_robots(self):
        r = self.client.get(reverse('robots'))
        assert r.status_code == 200

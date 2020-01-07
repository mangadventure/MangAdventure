from os import makedirs
from shutil import rmtree

from django.conf import settings
from django.test import Client

from pytest import mark


@mark.django_db
class MangadvTestBase:
    @classmethod
    def setup_class(cls):
        makedirs(settings.MEDIA_ROOT, exist_ok=True)

    def setup_method(self):
        self.client = Client()

    def teardown_method(self):
        pass

    @classmethod
    def teardown_class(cls):
        rmtree(settings.MEDIA_ROOT)

from django.test import Client

import pytest


@pytest.mark.django_db
class MangadvTestBase:
    def setup_method(self):
        self.client = Client()

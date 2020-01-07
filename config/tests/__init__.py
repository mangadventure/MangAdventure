from django.contrib.auth.models import User

from pytest import mark

from MangAdventure.tests.base import MangadvTestBase


@mark.usefixtures('django_db_setup')
class ConfigTestBase(MangadvTestBase):
    def setup_method(self):
        super().setup_method()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

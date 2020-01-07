from django.contrib.auth.models import User

from pytest import mark

from MangAdventure.tests.base import MangadvTestBase

from reader.models import Series


@mark.usefixtures('django_db_setup')
class UsersTestBase(MangadvTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.get(pk=1)
        self.user = User.objects.get(pk=1)

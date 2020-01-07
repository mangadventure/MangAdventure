from pytest import mark

from MangAdventure.tests.base import MangadvTestBase


@mark.usefixtures('django_db_setup')
class GroupsTestBase(MangadvTestBase):
    def setup_method(self):
        super().setup_method()

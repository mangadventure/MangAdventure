import pytest

from MangAdventure.tests import MangadvTestBase


@pytest.mark.usefixtures("django_db_setup")
class GroupsTestBase(MangadvTestBase):
    def setup_method(self):
        super().setup_method()

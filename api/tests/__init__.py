import pytest

from MangAdventure.tests import MangadvTestBase


@pytest.mark.usefixtures("django_db_setup")
class APITestBase(MangadvTestBase):
    pass

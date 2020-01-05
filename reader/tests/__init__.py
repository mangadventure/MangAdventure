from pytest import mark

from MangAdventure.tests.base import MangadvTestBase


@mark.usefixtures('django_db_setup')
class ReaderTestBase(MangadvTestBase):
    pass

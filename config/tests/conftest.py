from pathlib import Path

from django.core.management import call_command

import pytest


@pytest.fixture(scope='class')
def django_db_setup(django_db_setup, django_db_blocker):
    fixtures_dir = Path(__file__).parent / "fixtures"
    user_fixture = fixtures_dir / "users.json"
    with django_db_blocker.unblock():
        call_command('loaddata', str(user_fixture.resolve()))

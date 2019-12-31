from pathlib import Path

from django.core.management import call_command

import pytest


@pytest.fixture(scope='class')
def django_db_setup(django_db_setup, django_db_blocker):
    fixtures_dir = Path(__file__).parent / "fixtures"
    series_fixture = fixtures_dir / "series.yaml"
    chapters_fixture = fixtures_dir / "chapters.yaml"
    authors_artists_fixture = fixtures_dir / "authors_artists.yaml"
    groups_fixture = fixtures_dir / "groups.yaml"
    with django_db_blocker.unblock():
        call_command('loaddata', "categories.yaml")
        call_command('loaddata', str(authors_artists_fixture.resolve()))
        call_command('loaddata', str(groups_fixture.resolve()))
        call_command('loaddata', str(series_fixture.resolve()))
        call_command('loaddata', str(chapters_fixture.resolve()))

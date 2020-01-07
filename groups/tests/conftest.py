from django.core.management import call_command

from pytest import fixture


@fixture(scope='class')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('flush', '--no-input')

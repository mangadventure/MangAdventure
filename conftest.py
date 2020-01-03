import pytest

from MangAdventure.tests import media_dir


@pytest.fixture
def custom_test_settings(settings):
    settings.MEDIA_ROOT = media_dir
    settings.SECURE_SSL_REDIRECT = False
    settings.DEBUG = False
    yield

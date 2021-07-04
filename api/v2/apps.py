"""App configuration."""

from django.apps import AppConfig


class ApiV2Config(AppConfig):
    """Configuration for the api.v2 app."""
    #: The name of the app.
    name = 'api.v2'


__all__ = ['ApiV2Config']

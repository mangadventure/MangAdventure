"""App configuration."""

from django.apps import AppConfig


class ApiV1Config(AppConfig):
    """Configuration for the api.v1 app."""
    #: The name of the app.
    name = 'api.v1'


__all__ = ['ApiV1Config']

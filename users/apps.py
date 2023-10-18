"""App configuration."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the users app."""
    #: The name of the app.
    name = 'users'


__all__ = ['UsersConfig']

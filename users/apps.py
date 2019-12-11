"""App configuration."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the users app."""
    #: The name of the app.
    name = 'users'

    def ready(self):
        """Register the :mod:`~users.receivers` when the app is ready."""
        __import__('users.receivers')
        super(UsersConfig, self).ready()


__all__ = ['UsersConfig']

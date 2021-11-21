"""App configuration."""

from django.apps import AppConfig


class ReaderConfig(AppConfig):
    """Configuration for the users app."""
    #: The name of the app.
    name = 'reader'

    def ready(self):
        """Register the :mod:`~reader.receivers` when the app is ready."""
        __import__('reader.receivers')
        super().ready()


__all__ = ['ReaderConfig']

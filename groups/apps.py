"""App configuration."""

from django.apps import AppConfig


class GroupsConfig(AppConfig):
    """Configuration for the groups app."""
    #: The name of the app.
    name = 'groups'


__all__ = ['GroupsConfig']

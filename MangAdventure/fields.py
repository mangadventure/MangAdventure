"""Custom database models & model fields."""

from django.db.models import CharField, URLField

from .validators import (
    discord_name_validator, discord_server_validator,
    reddit_name_validator, twitter_name_validator
)


class TwitterField(CharField):
    """A :class:`~django.db.models.CharField` for Twitter usernames."""
    default_validators = (twitter_name_validator,)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 15
        super().__init__(*args, **kwargs)


class DiscordNameField(CharField):
    """A :class:`~django.db.models.CharField` for Discord usernames."""
    default_validators = (discord_name_validator,)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 37
        super().__init__(*args, **kwargs)


class RedditField(CharField):
    """A :class:`~django.db.models.CharField` for Reddit names."""
    default_validators = (reddit_name_validator,)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 21)
        super().__init__(*args, **kwargs)


class DiscordURLField(URLField):
    """A :class:`~django.db.models.CharField` for Discord server URLs."""
    default_validators = (discord_server_validator,)


__all__ = ['TwitterField', 'DiscordNameField', 'DiscordURLField', 'RedditField']

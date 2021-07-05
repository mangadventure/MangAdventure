"""Custom database models & model fields."""

from django.db.models import CharField, URLField

from .validators import (
    DiscordNameValidator, DiscordServerValidator,
    RedditNameValidator, TwitterNameValidator
)


class TwitterField(CharField):
    """A :class:`~django.db.models.CharField` for Twitter usernames."""
    default_validators = (TwitterNameValidator,)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 15
        super().__init__(*args, **kwargs)


class DiscordNameField(CharField):
    """A :class:`~django.db.models.CharField` for Discord usernames."""
    default_validators = (DiscordNameValidator,)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 37
        super().__init__(*args, **kwargs)


class RedditField(CharField):
    """A :class:`~django.db.models.CharField` for Reddit names."""
    default_validators = (RedditNameValidator,)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 21)
        super().__init__(*args, **kwargs)


class DiscordURLField(URLField):
    """A :class:`~django.db.models.CharField` for Discord server URLs."""
    default_validators = (DiscordServerValidator,)


__all__ = ['TwitterField', 'DiscordNameField', 'DiscordURLField', 'RedditField']

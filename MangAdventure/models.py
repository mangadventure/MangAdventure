"""Custom database models & model fields."""

from django.db import models

from . import validators


class TwitterField(models.CharField):
    """A :class:`~django.db.models.CharField` for Twitter usernames."""
    default_validators = (validators.twitter_name_validator,)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 15
        super(TwitterField, self).__init__(*args, **kwargs)


class DiscordNameField(models.CharField):
    """A :class:`~django.db.models.CharField` for Discord usernames."""
    default_validators = (validators.discord_name_validator,)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 37
        super(DiscordNameField, self).__init__(*args, **kwargs)


class RedditField(models.CharField):
    """A :class:`~django.db.models.CharField` for Reddit names."""
    default_validators = (validators.reddit_name_validator,)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 21)
        super(RedditField, self).__init__(*args, **kwargs)


class DiscordURLField(models.URLField):
    """A :class:`~django.db.models.CharField` for Discord server URLs."""
    default_validators = (validators.discord_server_validator,)


class AliasField(models.CharField):
    """A :class:`~django.db.models.CharField` for aliases."""
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        kwargs['unique'] = True
        kwargs.setdefault('max_length', 100)
        super(AliasField, self).__init__(*args, **kwargs)


class AliasKeyField(models.ForeignKey):
    """A :class:`~django.db.models.ForeignKey` for aliases."""
    def __init__(self, *args, **kwargs):
        kwargs['related_name'] = 'aliases'
        kwargs['on_delete'] = models.CASCADE
        super(AliasKeyField, self).__init__(*args, **kwargs)


class Alias(models.Model):
    """An abstract :class:`~django.db.models.Model` for aliases."""
    alias: AliasField

    class Meta:
        abstract = True
        verbose_name = 'alias'
        verbose_name_plural = 'aliases'

    def __str__(self) -> str:
        """Return the alias of the instance."""
        return self.alias or ''


__all__ = [
    'TwitterField', 'DiscordNameField', 'DiscordURLField',
    'RedditField', 'AliasField', 'AliasKeyField', 'Alias'
]

from django.db import models
from .utils import validators


class TwitterField(models.CharField):
    default_validators = [validators.twitter_name_validator]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 15
        super(TwitterField, self).__init__(*args, **kwargs)


class DiscordNameField(models.CharField):
    default_validators = [validators.discord_name_validator]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 37
        super(DiscordNameField, self).__init__(*args, **kwargs)


class DiscordURLField(models.URLField):
    default_validators = [validators.discord_server_validator]

    def __init__(self, *args, **kwargs):
        super(DiscordURLField, self).__init__(*args, **kwargs)


class AliasField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 100)
        kwargs['blank'] = True
        kwargs['unique'] = True
        super(AliasField, self).__init__(*args, **kwargs)


class AliasKeyField(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['related_name'] = 'aliases'
        kwargs['on_delete'] = models.CASCADE
        super(AliasKeyField, self).__init__(*args, **kwargs)


class Alias(models.Model):
    alias = None

    class Meta:
        abstract = True
        verbose_name = 'alias'
        verbose_name_plural = verbose_name + 'es'

    def __str__(self): return self.alias


__all__ = [
    'TwitterField', 'DiscordNameField',
    'DiscordURLField', 'AliasField',
    'AliasKeyField', 'Alias'
]


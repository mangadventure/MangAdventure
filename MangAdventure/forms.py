"""Custom form fields."""

from django.forms import CharField, URLField

from MangAdventure import validators


class TwitterField(CharField):
    """A :class:`~django.forms.CharField` for Twitter usernames."""
    default_validators = (validators.TwitterNameValidator,)


class DiscordURLField(URLField):
    """A :class:`~django.forms.URLField` for Discord server URLs."""
    default_validators = (validators.DiscordServerValidator,)


__all__ = ['TwitterField', 'DiscordURLField']

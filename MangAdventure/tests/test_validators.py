from django.forms import ValidationError

from pytest import raises

from MangAdventure.validators import (
    DiscordNameValidator, RedditNameValidator, TwitterNameValidator
)


def test_discord_name():
    validate = DiscordNameValidator()
    validate('Epic_user-123#8910')
    with raises(ValidationError):
        validate('User')
    with raises(ValidationError):
        validate('User8910')


def test_reddit_name():
    validate = RedditNameValidator()
    validate('/u/epicuser_1234')
    validate('/r/epicsub_1234')
    validate('epicuser_1234')
    with raises(ValidationError):
        validate('/u/epic-user_1234')


def test_twitter_name():
    validate = TwitterNameValidator()
    validate('Epic_user-1234')
    with raises(ValidationError):
        validate('@Epic_user-1234')

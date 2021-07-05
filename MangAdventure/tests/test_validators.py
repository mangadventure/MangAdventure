from django.forms import ValidationError

from pytest import raises

from MangAdventure.validators import (
    DiscordNameValidator, RedditNameValidator, TwitterNameValidator
)


def test_discord_name():
    DiscordNameValidator('Epic_user-123#8910')
    with raises(ValidationError):
        DiscordNameValidator('User')
    with raises(ValidationError):
        DiscordNameValidator('User8910')


def test_reddit_name():
    RedditNameValidator('/u/epicuser_1234')
    RedditNameValidator('/r/epicsub_1234')
    RedditNameValidator('epicuser_1234')
    with raises(ValidationError):
        RedditNameValidator('/u/epic-user_1234')


def test_twitter_name():
    TwitterNameValidator('Epic_user-1234')
    with raises(ValidationError):
        TwitterNameValidator('@Epic_user-1234')

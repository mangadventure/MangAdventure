from django.forms import ValidationError

from pytest import raises

from MangAdventure.validators import (
    discord_name_validator, reddit_name_validator, twitter_name_validator
)


def test_discord_name():
    discord_name_validator('Epic_user-123#8910')
    with raises(ValidationError):
        discord_name_validator('User')
    with raises(ValidationError):
        discord_name_validator('User8910')


def test_reddit_name():
    reddit_name_validator('/u/epicuser_1234')
    reddit_name_validator('/r/epicsub_1234')
    reddit_name_validator('epicuser_1234')
    with raises(ValidationError):
        reddit_name_validator('/u/epic-user_1234')


def test_twitter_name():
    twitter_name_validator('Epic_user-1234')
    with raises(ValidationError):
        twitter_name_validator('@Epic_user-1234')

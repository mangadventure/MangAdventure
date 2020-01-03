from django.forms import Form

from MangAdventure.forms import DiscordURLField, TwitterField


class FormTest(Form):
    twitter = TwitterField(required=False)
    discord = DiscordURLField(required=False)


def test_twitter_valid():
    form = FormTest(data={'twitter': 'name123'})
    assert form.is_valid()


def test_twitter_invalid():
    form = FormTest(data={'twitter': '@Test123'})
    assert not form.is_valid()


def test_discord_valid():
    form = FormTest(data={'discord': 'https://discord.gg/abc123'})
    assert form.is_valid()
    form = FormTest(data={'discord': 'https://discord.me/abc123'})
    assert form.is_valid()


def test_discord_invalid():
    form = FormTest(data={'discord': 'https://other.eu/test'})
    assert not form.is_valid()

"""Serializers for the users app."""

from typing import Dict, List

from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator

from rest_framework.fields import (
    CharField, CurrentUserDefault, EmailField, HiddenField, URLField
)
from rest_framework.pagination import BasePagination
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from reader.models import Series

from .models import Bookmark, UserProfile


class BookmarkPagination(BasePagination):
    """Fake pagination class to adapt the bookmarks list schema."""
    def to_html(self) -> str:
        return ''

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        return {
            'type': 'object',
            'properties': {
                'rss': {
                    'type': 'string',
                    'format': 'uri'
                },
                'atom': {
                    'type': 'string',
                    'format': 'uri'
                },
                'bookmarks': schema
            }
        }


class BookmarkSerializer(ModelSerializer):
    """Serializer for bookmarks."""
    series = SlugRelatedField(
        queryset=Series.objects.only('id', 'slug'),
        slug_field='slug', help_text='The slug of the series.'
    )
    user = HiddenField(default=CurrentUserDefault())

    def get_validators(self) -> List:
        validators = super().get_validators()
        validators[0].message = 'This bookmark already exists.'
        return validators

    class Meta:
        model = Bookmark
        fields = ('series', 'user')


class ProfileSerializer(ModelSerializer):
    """Serializer for user profiles."""
    username = CharField(
        source='user.username', min_length=1, max_length=150,
        required=True, help_text='Your (unique) username.',
        validators=(UnicodeUsernameValidator(),),

    )
    first_name = CharField(
        source='user.first_name', max_length=150,
        required=False, help_text='Your first name.'
    )
    last_name = CharField(
        source='user.last_name', max_length=150,
        required=False, help_text='Your last name.'
    )
    email = EmailField(
        source='user.email', min_length=5, max_length=254,
        required=True, help_text='Your e-mail address.'
    )
    password = CharField(
        source='user.password', min_length=8, max_length=128,
        required=False, write_only=True, style={'input_type': 'password'},
        help_text='You can set this if you want to change your password.'
    )
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of your profile.'
    )

    def validate_username(self, value: str) -> str:
        if not value:
            return ''
        users = User.objects.filter(username=value)
        if users.exclude(id=self.context['request'].user.id).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('This username is already taken.')
        return value

    class Meta:
        model = UserProfile
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'bio', 'avatar', 'password', 'url',
        )
        extra_kwargs = {
            'bio': {
                'help_text': 'Some info about yourself.', 'label': None
            },
            'avatar': {
                'help_text': 'Your avatar image. (<2MBs)', 'allow_null': True
            }
        }


__all__ = ['BookmarkPagination', 'BookmarkSerializer', 'ProfileSerializer']

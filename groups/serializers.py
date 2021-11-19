"""
Model serializers for the groups app.

.. admonition:: TODO
   :class: warning

   Add a serializer for members.
"""

from typing import Dict, List

from rest_framework.fields import RegexField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from MangAdventure.validators import (
    DiscordServerValidator, RedditNameValidator, TwitterNameValidator
)

from .models import Group


class GroupSerializer(ModelSerializer):
    """Serializer for groups."""
    discord = RegexField(
        regex=DiscordServerValidator.regex, required=False,
        help_text="The group's Discord link.", max_length=200
    )
    twitter = RegexField(
        regex=TwitterNameValidator.regex, required=False,
        help_text="The group's Twitter username.", max_length=15
    )
    reddit = RegexField(
        regex=RedditNameValidator.regex, required=False,
        help_text="The group's Reddit username or subreddit.", max_length=24
    )
    members = SerializerMethodField(
        help_text='The members of this group.', method_name='_get_members'
    )

    def _get_members(self, obj: Group) -> List[str]:
        return [f'{m} ({m.get_roles(obj)})' for m in obj.members.distinct()]

    def create(self, validated_data: Dict) -> Group:
        """Create a new ``Group`` instance."""
        # manually set the manager to the current user
        return super().create({
            **validated_data,
            'manager_id': self.context['request'].user.id
        })

    class Meta:
        model = Group
        fields = (
            'id', 'name', 'website', 'description', 'email',
            'discord', 'twitter', 'reddit', 'irc', 'logo', 'members',
        )
        extra_kwargs = {
            'id': {
                'read_only': True, 'min_value': 1,
                'help_text': 'The unique ID of the group.'
            }
        }


__all__ = ['GroupSerializer']

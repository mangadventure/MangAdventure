"""Model serializers for the groups app."""

from rest_framework.fields import RegexField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from MangAdventure.validators import (
    DiscordNameValidator, DiscordServerValidator,
    RedditNameValidator, TwitterNameValidator
)

from .models import Group, Member


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

    def _get_members(self, obj: Group) -> list[str]:
        return [
            f'{r.get_role_display()}: {r.member.name}'
            for r in obj.roles.all()
        ]

    def create(self, validated_data: dict) -> Group:
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


class MemberSerializer(ModelSerializer):
    """Serializer for members."""
    twitter = RegexField(
        regex=TwitterNameValidator.regex, required=False,
        help_text="The member's Twitter username.", max_length=15
    )
    discord = RegexField(
        regex=DiscordNameValidator.regex, required=False, max_length=37,
        help_text="The member's Discord name and discriminator."
    )
    reddit = RegexField(
        regex=RedditNameValidator.regex, required=False,
        help_text="The member's Reddit username.", max_length=21
    )
    groups = SerializerMethodField(
        help_text='The groups this person belongs to.',
        method_name='_get_groups'
    )

    def _get_groups(self, obj: Member) -> list[str]:
        return [
            f'{g.name} ({obj.get_roles(g)})' for g
            in obj.groups.only('id', 'name').distinct()
        ]

    class Meta:
        model = Member
        fields = (
            'id', 'name', 'twitter', 'discord',
            'irc', 'reddit', 'groups'
        )


__all__ = ['GroupSerializer', 'MemberSerializer']

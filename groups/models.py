"""Database models for the groups app."""

from __future__ import annotations

from enum import Enum, EnumMeta
from pathlib import PurePath

from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Coalesce
from django.shortcuts import reverse

from MangAdventure.fields import (
    DiscordNameField, DiscordURLField, RedditField, TwitterField
)
from MangAdventure.storage import CDNStorage
from MangAdventure.validators import FileSizeValidator


def _logo_uploader(obj: Group, name: str) -> str:
    name = f'logo.{name.split(".")[-1]}'
    return str(obj.get_directory() / name)


class _ChoiceMeta(EnumMeta):
    def __new__(cls, name, bases, attrs):
        klass = super().__new__(cls, name, (Enum,) + bases, attrs)
        klass.do_not_call_in_templates = True
        klass.__str__ = lambda self: self.name
        return klass

    def __iter__(cls):
        return ((e.name, e.value) for e in super().__iter__())


class Group(models.Model):
    """A model representing a group."""
    #: The group's ID.
    id = models.SmallIntegerField(primary_key=True, auto_created=True)
    #: The group's name.
    name = models.CharField(max_length=100, help_text="The group's name.")
    #: The group's website.
    website = models.URLField(blank=True, help_text="The group's website.")
    #: The group's description.
    description = models.TextField(
        blank=True, help_text='A description for the group.'
    )
    #: The group's e-mail address.
    email = models.EmailField(
        blank=True, help_text="The group's E-mail address."
    )
    #: The Discord server URL of the group.
    discord = DiscordURLField(
        blank=True, help_text="The group's Discord link."
    )
    #: The Twitter username of the group.
    twitter = TwitterField(
        blank=True, help_text="The group's Twitter username."
    )
    #: The group's IRC.
    irc = models.CharField(
        max_length=63, blank=True, help_text="The group's IRC."
    )
    #: The Reddit username or subreddit name of the group.
    reddit = RedditField(
        max_length=24, blank=True,
        help_text="The group's Reddit username or "
                  "subreddit. (Include /u/ or /r/)"
    )
    #: The group's logo.
    logo = models.ImageField(
        blank=True, storage=CDNStorage((150, 150)),
        upload_to=_logo_uploader, validators=(FileSizeValidator(2),),
        help_text="Upload the group's logo. Its size must not exceed 2 MBs.",
    )
    #: The person who manages this group.
    manager = models.ForeignKey(
        User, editable=True, blank=False, null=True,
        help_text='The person who manages this group.',
        on_delete=models.SET_NULL, limit_choices_to=(
            models.Q(is_superuser=True) | models.Q(groups__name='Scanlator')
        )
    )

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`groups.views.group`.
        """
        return reverse('groups:group', args=(self.id,))

    def get_directory(self) -> PurePath:
        """
        Get the storage directory of the object.

        :return: A path relative to
                 :const:`~MangAdventure.settings.MEDIA_ROOT`.
        """
        return PurePath('groups', str(self.id))

    @property
    def _increment(self) -> int:
        return Group.objects.aggregate(
            last=Coalesce(models.Max('id'), 0) + 1
        )['last']

    def save(self, *args, **kwargs):
        """Save the current instance."""
        if not self.id:
            self.id = self._increment
        super(Group, self).save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the group.
        """
        return self.name


class Member(models.Model):
    """A model representing a member."""
    #: The name of the member.
    name = models.CharField(max_length=100, help_text="The member's name.")
    #: The member's Twitter username.
    twitter = TwitterField(
        blank=True, help_text="The member's Twitter username."
    )
    #: The member's Discord username and discriminator.
    discord = DiscordNameField(blank=True, help_text=(
        "The member's Discord username and discriminator."
    ))
    #: The member's IRC username.
    irc = models.CharField(
        max_length=63, blank=True, help_text="The member's IRC username."
    )
    #: The member's Reddit username.
    reddit = RedditField(
        blank=True, help_text="The member's Reddit username."
    )
    #: The groups of this member.
    groups = models.ManyToManyField(Group, 'members', through='Role')

    def get_roles(self, group: Group) -> str:
        """
        Get the roles of the member in the given group.

        :param group: A group instance.
        :return: A comma-separated list of roles.
        """
        return ', '.join(
            r.get_role_display() for r in
            self.roles.filter(group_id=group.id).only('role')
        )

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the member.
        """
        return self.name


class Role(models.Model):
    """A model representing a role."""

    class Choices(metaclass=_ChoiceMeta):
        """The possible role choices."""
        LD = 'Leader'
        TL = 'Translator'
        PR = 'Proofreader'
        CL = 'Cleaner'
        RD = 'Redrawer'
        TS = 'Typesetter'
        RP = 'Raw Provider'
        QC = 'Quality Checker'

    #: The member this role belongs to.
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='roles'
    )
    #: The group this role belongs to.
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='roles'
    )
    #: The value of the role.
    role = models.CharField(blank=False, max_length=2, choices=Choices)

    class Meta:
        verbose_name = 'role'
        unique_together = ('member', 'role', 'group')

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name and group of the role.
        """
        return f'{self.get_role_display()} ({self.group})'


__all__ = ['Group', 'Member', 'Role']

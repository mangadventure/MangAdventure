"""Database models for the groups app."""

from pathlib import PurePath

from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property

from MangAdventure.models import (
    DiscordNameField, DiscordURLField, RedditField, TwitterField
)
from MangAdventure.utils.images import thumbnail
from MangAdventure.utils.storage import OverwriteStorage
from MangAdventure.utils.validators import FileSizeValidator


def _logo_uploader(obj: 'Group', name: str) -> str:
    name = f'logo.{name.split(".")[-1]}'
    return str(obj.get_directory() / name)


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
    discord = DiscordURLField(blank=True, help_text="The group's Discord link.")
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
        blank=True, upload_to=_logo_uploader,
        storage=OverwriteStorage(), validators=(FileSizeValidator(2),),
        help_text="Upload the group's logo. Its size must not exceed 2 MBs.",
    )

    @cached_property
    def members(self) -> models.QuerySet:
        """Get the members of the group."""
        return Member.objects.filter(id__in=models.Subquery(
            Role.objects.filter(group_id=self.id).values('member')
        ))

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
        try:
            num = Group.objects.only('id').last().id + 1
        except (Group.DoesNotExist, AttributeError):
            num = 1
        return num

    def save(self, *args, **kwargs):
        """Save the current instance."""
        if not self.id:
            self.id = self._increment
        if self.logo:
            self.logo = thumbnail(self.logo, 150)
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

    @cached_property
    def groups(self) -> models.QuerySet:
        """Get the groups of the member."""
        return Group.objects.filter(id__in=models.Subquery(
            Role.objects.filter(member_id=self.id).values('group')
        ))

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the member.
        """
        return self.name


class Role(models.Model):
    """A model representing a role."""
    #: A list of possible role choices.
    #:
    #: The first element of each tuple is the value and
    #: the second is its human-readable representation.
    ROLES = [
        ('LD', 'Leader'),
        ('TL', 'Translator'),
        ('PR', 'Proofreader'),
        ('CL', 'Cleaner'),
        ('RD', 'Redrawer'),
        ('TS', 'Typesetter'),
        ('RP', 'Raw Provider'),
        ('QC', 'Quality Checker')
    ]
    #: The member this role belongs to.
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='roles'
    )
    #: The group this role belongs to.
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='roles'
    )
    #: The value of the role.
    role = models.CharField(blank=False, max_length=2, choices=ROLES)

    class Meta:
        verbose_name = 'Role'
        unique_together = ('member', 'role', 'group')

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name and group of the role.
        """
        return f'{self.get_role_display()} {(self.group)}'


__all__ = ['Group', 'Member', 'Role']

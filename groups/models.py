from django.db import models
from django.shortcuts import reverse

from MangAdventure.models import (
    DiscordNameField, DiscordURLField, RedditField, TwitterField
)
from MangAdventure.utils.images import thumbnail
from MangAdventure.utils.storage import OverwriteStorage
from MangAdventure.utils.uploaders import group_logo_uploader
from MangAdventure.utils.validators import FileSizeValidator


class Group(models.Model):
    _help = "The group's %s."
    id = models.SmallIntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, help_text=_help % 'name')
    website = models.URLField(blank=True, help_text=_help % 'website')
    description = models.TextField(
        blank=True, help_text='A description for the group.'
    )
    email = models.EmailField(blank=True, help_text=_help % 'E-mail address')
    discord = DiscordURLField(blank=True, help_text=_help % 'Discord link')
    twitter = TwitterField(blank=True, help_text=_help % 'Twitter username')
    irc = models.CharField(max_length=63, blank=True, help_text=_help % 'IRC')
    reddit = RedditField(
        max_length=24, blank=True,
        help_text="The group's Reddit username or "
                  "subreddit. (Include /u/ or /r/)"
    )
    logo = models.ImageField(
        blank=True, upload_to=group_logo_uploader,
        storage=OverwriteStorage(), validators=(FileSizeValidator(max_mb=2),),
        help_text="Upload the group's logo. Its size must not exceed 2 MBs.",
    )

    @property
    def members(self):
        return Member.objects.filter(id__in=models.Subquery(
            Role.objects.filter(group_id=self.id).values('member')
        ))

    def get_absolute_url(self):
        return reverse('groups:group', args=(self.id,))

    @property
    def _increment(self):
        try:
            num = Group.objects.only('id').last().id + 1
        except (Group.DoesNotExist, AttributeError):
            num = 1
        return num

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self._increment
        if self.logo:
            self.logo = thumbnail(self.logo, 150)
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Member(models.Model):
    _help = "The member's %s."
    name = models.CharField(max_length=100, help_text=_help % 'name')
    twitter = TwitterField(blank=True, help_text=_help % 'Twitter username')
    discord = DiscordNameField(
        blank=True, help_text=_help % 'Discord username and discriminator'
    )
    irc = models.CharField(
        max_length=63, blank=True, help_text=_help % 'IRC username'
    )
    reddit = RedditField(
        blank=True, help_text=_help % 'Reddit username'
    )

    @property
    def groups(self):
        return Group.objects.filter(id__in=models.Subquery(
            Role.objects.filter(member_id=self.id).values('group')
        ))

    def __str__(self):
        return self.name


class Role(models.Model):
    ROLES = (
        ('LD', 'Leader'),
        ('TL', 'Translator'),
        ('PR', 'Proofreader'),
        ('CL', 'Cleaner'),
        ('RD', 'Redrawer'),
        ('TS', 'Typesetter'),
        ('RP', 'Raw Provider'),
        ('QC', 'Quality Checker')
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='roles'
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='roles'
    )
    role = models.CharField(blank=False, max_length=2, choices=ROLES)

    class Meta:
        verbose_name = 'Role'
        unique_together = ('member', 'role', 'group')

    def __str__(self):
        return f'{self.get_role_display()} {(self.group)}'


__all__ = ['Group', 'Member', 'Role']

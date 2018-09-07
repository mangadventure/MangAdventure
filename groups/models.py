from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from MangAdventure.utils.storage import OverwriteStorage
from MangAdventure.utils.uploaders import group_logo_uploader
from MangAdventure.utils.validators import FileSizeValidator
from MangAdventure.utils.images import thumbnail
from MangAdventure.models import *


class Group(models.Model):
    _help = "The group's %s."
    id = models.SmallIntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, help_text=_help % 'name')
    website = models.URLField(help_text=_help % 'website')
    email = models.EmailField(blank=True, help_text=_help % 'E-mail address')
    discord = DiscordURLField(blank=True, help_text=_help % 'Discord link')
    twitter = TwitterField(blank=True, help_text=_help % 'Twitter username')
    description = models.TextField(blank=True,
                                   help_text='A description for the group.')
    logo = models.ImageField(blank=True, storage=OverwriteStorage(),
                             upload_to=group_logo_uploader,
                             help_text="Upload the group's logo."
                                       " Its size must not exceed 2 MBs.",
                             validators=[FileSizeValidator(max_mb=2)])

    @property
    def _increment(self):
        try:
            num = Group.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            num = 1
        return num

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self._increment
        if self.logo:
            self.logo = thumbnail(self.logo, 150)
        super(Group, self).save(*args, **kwargs)

    def __str__(self): return self.name


class Member(models.Model):
    _help = "The member's %s."
    name = models.CharField(max_length=100, help_text=_help % 'name')
    twitter = TwitterField(blank=True, help_text=_help % 'Twitter username')
    discord = DiscordNameField(blank=True,
                               help_text=_help % 'Discord username '
                                                 'and discriminator')

    def __str__(self): return self.name


class Role(models.Model):
    ROLES = [
        ('LD', 'Leader'),
        ('TL', 'Translator'),
        ('PR', 'Proofreader'),
        ('CL', 'Cleaner'),
        ('RD', 'Redrawer'),
        ('TS', 'Typesetter'),
        ('RP', 'Raw Provider'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE,
                               related_name='roles')
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              related_name='roles')
    role = models.CharField(blank=False, max_length=2, choices=ROLES)

    class Meta:
        verbose_name = 'Role'
        unique_together = ('member', 'role', 'group')
      
    def __str__(self):
        return '%s (%s)' % (self.get_role_display(), self.group)


__all__ = ['Group', 'Member', 'Role']


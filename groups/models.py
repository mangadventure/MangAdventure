from django.db import models
from MangAdventure.modules.storage import OverwriteStorage
from MangAdventure.modules.uploaders import group_logo_uploader, member_avatar_uploader
from MangAdventure.modules.validators import FileSizeValidator


class Group(models.Model):
    name = models.CharField(max_length=250,
                            help_text="The group's proper name.")
    website = models.URLField(help_text="The group's website.")
    email = models.EmailField(blank=True,
                              help_text="The group's contact e-mail address.")
    discord = models.URLField(blank=True,
                              help_text="Invite link for the group's discord guild.")
    twitter = models.CharField(max_length=15,
                               blank=True,
                               help_text="The group's twitter handle.")
    description = models.TextField(blank=True,
                                   help_text="The description of the group.")
    logo = models.ImageField(storage=OverwriteStorage(),
                             upload_to=group_logo_uploader,
                             help_text='Upload a group logo.'
                                       ' Its size must not exceed 2 MBs.',
                             validators=[FileSizeValidator(max_mb=2)])

    def __str__(self):
        return self.name


class Member(models.Model):
    name = models.CharField(max_length=100,
                            help_text="The member's name.")
    twitter = models.CharField(max_length=15,
                               blank=True,
                               help_text="The member's twitter handle.")
    discord = models.CharField(max_length=32,
                               blank=True,
                               help_text="The member's discord name (and id).")
    avatar = models.ImageField(storage=OverwriteStorage(),
                               upload_to=member_avatar_uploader,
                               help_text='Upload a member avatar.'
                                         ' Its size must not exceed 2 MBs.',
                               validators=[FileSizeValidator(max_mb=2)])
    groups = models.ManyToManyField(Group, blank=True, related_name='members')

    def __str__(self):
        return self.name


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

    role = models.CharField(max_length=2, choices=ROLES)
    member = models.ForeignKey(Member, on_delete=models.CASCADE,
                               related_name='roles')

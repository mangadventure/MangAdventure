from os.path import join
from shutil import move
from time import mktime

from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django.utils.http import http_date
from django.utils.text import slugify

from groups.models import Group
from MangAdventure.models import Alias, AliasField, AliasKeyField
from MangAdventure.utils import images, storage, uploaders, validators


def _move(old, new):
    try:
        move(old.get_directory, new.get_directory)
    except OSError as e:
        if e.errno == 2: pass
        else: raise e


def _alias_help(name, identifier='name'):
    return 'Another %s for the %s.' % (identifier, name)


class Author(models.Model):
    name = models.CharField(
        max_length=100, help_text="The author's full name."
    )

    def __str__(self): return self.name


class Artist(models.Model):
    name = models.CharField(
        max_length=100, help_text="The artist's full name."
    )

    def __str__(self): return self.name


class Category(models.Model):
    id = models.CharField(
        primary_key=True, default='', max_length=25, auto_created=True
    )
    name = models.CharField(
        max_length=25, unique=True,
        help_text='The name of the category. Must be '
                  'unique and cannot be changed once set.'
    )
    description = models.CharField(
        max_length=250, help_text='A description for the category.'
    )

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        self.id = self.name.lower()
        super(Category, self).save(*args, **kwargs)

    def __str__(self): return self.name


class Series(models.Model):
    _validator = validators.FileSizeValidator(max_mb=2)
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=250, help_text='The title of the series.'
    )
    slug = models.SlugField(
        blank=True, unique=True, verbose_name='Custom slug',
        help_text='The unique slug of the series. Will be used in the URL.'
    )
    description = models.TextField(
        blank=True, help_text='The description of the series.'
    )
    cover = models.ImageField(
        storage=storage.OverwriteStorage(),
        upload_to=uploaders.cover_uploader,
        help_text='Upload a cover image for the series. Its size '
                  'must not exceed %d MBs.' % _validator.max_mb,
        validators=[_validator]
    )
    authors = models.ManyToManyField(Author, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    completed = models.BooleanField(
        default=False, help_text='Is the series completed?'
    )
    modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('reader:series', args=[self.slug])

    def get_directory(self):
        return join('series', self.slug)

    class Meta:
        verbose_name_plural = 'series'
        get_latest_by = 'modified'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug or self.title)
        if self.cover:
            self.cover = images.thumbnail(self.cover, 300)
        super(Series, self).save(*args, **kwargs)

    def __str__(self): return self.title


class AuthorAlias(Alias):
    author = AliasKeyField(Author)
    alias = AliasField(help_text=_alias_help('author'))


class ArtistAlias(Alias):
    artist = AliasKeyField(Artist)
    alias = AliasField(help_text=_alias_help('artist'))


class SeriesAlias(Alias):
    series = AliasKeyField(Series)
    alias = AliasField(
        max_length=250, help_text=_alias_help('series', 'title')
    )


class Chapter(models.Model):
    _help = 'The %s of the chapter.'
    _vol_help = _help % 'volume' + ' Leave as 0 if the series has no volumes.'
    _file_help = (
        'Upload a zip or cbz file containing the chapter pages.',
        'Its size cannot exceed 50 MBs and it must not',
        'contain more than 1 subfolder.'
    )
    title = models.CharField(max_length=250, help_text=_help % 'title')
    number = models.FloatField(default=0, help_text=_help % 'number')
    volume = models.PositiveSmallIntegerField(default=0, help_text=_vol_help)
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name='chapters',
        help_text='The series this chapter belongs to.'
    )
    file = models.FileField(
        help_text=' '.join(_file_help), validators=[
            validators.FileSizeValidator(max_mb=50),
            validators.zipfile_validator
        ], blank=True
    )
    final = models.BooleanField(
        default=False, help_text='Is this the final chapter?'
    )
    uploaded = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(
        Group, blank=True, related_name='releases'
    )

    class Meta:
        unique_together = ('series', 'volume', 'number')
        ordering = ('series', 'volume', 'number')
        get_latest_by = ('uploaded', 'modified')

    def save(self, *args, **kwargs):
        super(Chapter, self).save(*args, **kwargs)
        if self.file:
            validators.zipfile_validator(self.file)
            Page.objects.filter(chapter=self).delete()
            images.unzip(self)
        self.series.completed = self.final
        self.series.save()

    @cached_property
    def get_uploaded_date(self):
        return http_date(mktime(self.uploaded.timetuple()))

    @cached_property
    def get_modified_date(self):
        return http_date(mktime(self.modified.timetuple()))

    def get_absolute_url(self):
        return reverse('reader:chapter', args=[
            self.series.slug, self.volume, '%g' % self.number
        ])

    def get_directory(self):
        return join(
            self.series.get_directory(), str(self.volume), '%g' % self.number
        )

    def __str__(self):
        return '{0.series.title} - {0.volume}/' \
               '{0.number:g}: {0.title}'.format(self)

    def __gt__(self, other):
        if self.volume == other.volume:
            return self.number > other.number
        return self.volume > other.volume

    def __lt__(self, other):
        if self.volume == other.volume:
            return self.number < other.number
        return self.volume < other.volume


class Page(models.Model):
    chapter = models.ForeignKey(
        Chapter, related_name='pages', on_delete=models.CASCADE
    )
    image = models.ImageField()
    number = models.PositiveSmallIntegerField()

    def get_file_name(self):
        return self.image.name.split('/')[-1]

    def get_absolute_url(self):
        return reverse('reader:page', args=[
            self.chapter.series.slug, self.chapter.volume,
            '%g' % self.chapter.number, self.number
        ])

    def __str__(self):
        return '{0.series.title} - {0.volume}/{0.number} [{1}]'.format(
            self.chapter, self.get_file_name
        )

    def __gt__(self, other): return self.number > other.number

    def __lt__(self, other): return self.number < other.number


__all__ = [
    'Author', 'AuthorAlias', 'Artist', 'ArtistAlias',
    'Series', 'SeriesAlias', 'Chapter', 'Page', 'Category'
]

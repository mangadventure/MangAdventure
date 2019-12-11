"""Database models for the reader app."""

from io import BytesIO
from os import path, remove
from pathlib import PurePath
from shutil import rmtree
from typing import Any, Tuple
from zipfile import ZipFile

from django.conf import settings
from django.db import models
from django.db.models.query import Q
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django.utils.http import http_date
from django.utils.text import slugify

from PIL import Image

from MangAdventure import storage, validators, utils
from MangAdventure.models import Alias, AliasField, AliasKeyField

from groups.models import Group


def _cover_uploader(obj: 'Series', name: str) -> str:
    name = f'cover.{name.split(".")[-1]}'
    return str(obj.get_directory() / name)


class Author(models.Model):
    """A model representing an author."""
    #: The name of the author.
    name = models.CharField(
        max_length=100, db_index=True,
        help_text="The author's full name."
    )

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the author.
        """
        return self.name


class Artist(models.Model):
    """A model representing an artist."""
    #: The name of the artist.
    name = models.CharField(
        max_length=100, db_index=True,
        help_text="The artist's full name."
    )

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the artist.
        """
        return self.name


class Category(models.Model):
    """A model representing a category."""
    #: The category's ID.
    id = models.CharField(
        primary_key=True, default='', max_length=25, auto_created=True
    )
    #: The unique name of the category.
    name = models.CharField(
        max_length=25, unique=True,
        help_text='The name of the category. Must be '
                  'unique and cannot be changed once set.'
    )
    #: The description of the category.
    description = models.CharField(
        max_length=250, help_text='A description for the category.'
    )

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        """Save the current instance."""
        if not self.id:
            self.id = self.name.lower()
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the category.
        """
        return self.name


class Series(models.Model):
    #: The series' ID.
    id = models.AutoField(primary_key=True)
    #: The title of the series.
    title = models.CharField(
        max_length=250, db_index=True, help_text='The title of the series.'
    )
    #: The unique slug of the series.
    slug = models.SlugField(
        blank=True, unique=True, verbose_name='Custom slug',
        help_text='The unique slug of the series. Will be used in the URL.'
    )
    #: The description of the series.
    description = models.TextField(
        blank=True, help_text='The description of the series.'
    )
    #: The cover image of the series.
    cover = models.ImageField(
        help_text=(
            'Upload a cover image for the series.'
            ' Its size must not exceed 2 MBs.'
        ), validators=(validators.FileSizeValidator(2),),
        storage=storage.OverwriteStorage(),
        upload_to=_cover_uploader
    )
    #: The authors of the series.
    authors = models.ManyToManyField(Author, blank=True)
    #: The artists of the series.
    artists = models.ManyToManyField(Artist, blank=True)
    #: The categories of the series.
    categories = models.ManyToManyField(Category, blank=True)
    #: The status of the series.
    completed = models.BooleanField(
        default=False, help_text='Is the series completed?'
    )
    #: The modification date of the series.
    modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`reader.views.series`.
        """
        return reverse('reader:series', args=(self.slug,))

    def get_directory(self) -> PurePath:
        """
        Get the storage directory of the object.

        :return: A path relative to
                 :const:`~MangAdventure.settings.MEDIA_ROOT`.
        """
        return PurePath('series', self.slug)

    class Meta:
        verbose_name_plural = 'series'
        get_latest_by = 'modified'

    def save(self, *args, **kwargs):
        """Save the current instance."""
        self.slug = slugify(self.slug or self.title)
        if self.cover:
            self.cover = utils.thumbnail(self.cover, 300)
        super(Series, self).save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The title of the series.
        """
        return self.title


class AuthorAlias(Alias):
    """A model representing an author's alias."""
    #: The author this alias belongs to.
    author = AliasKeyField(Author)
    #: The alias of the author.
    alias = AliasField(db_index=True, help_text='Another name for the author.')


class ArtistAlias(Alias):
    """A model representing an author's alias."""
    #: The artist this alias belongs to.
    artist = AliasKeyField(Artist)
    #: The alias of the artist.
    alias = AliasField(db_index=True, help_text='Another name for the artist.')


class SeriesAlias(Alias):
    """A model representing a series' alias."""
    #: The series this alias belongs to.
    series = AliasKeyField(Series)
    #: The alias of the series.
    alias = AliasField(
        max_length=250, db_index=True,
        help_text='Another title for the series.'
    )


class Chapter(models.Model):
    """A model representing a chapter."""
    #: The title of the chapter.
    title = models.CharField(
        max_length=250, help_text='The title of the chapter.'
    )
    #: The number of the chapter.
    number = models.FloatField(
        default=0, help_text='The number of the chapter.'
    )
    #: The volume of the chapter.
    volume = models.PositiveSmallIntegerField(default=0, help_text=(
        'The volume of the chapter. Leave as 0 if the series has no volumes.'
    ))
    #: The series this chapter belongs to.
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name='chapters',
        help_text='The series this chapter belongs to.'
    )
    #: The file which contains the chapter's pages.
    file = models.FileField(
        help_text=(
            'Upload a zip or cbz file containing the chapter pages.'
            ' Its size cannot exceed 50 MBs and it'
            ' must not contain more than 1 subfolder.'
        ), validators=(
            validators.FileSizeValidator(50),
            validators.zipfile_validator
        ), blank=True
    )
    #: The status of the chapter.
    final = models.BooleanField(
        default=False, help_text='Is this the final chapter?'
    )
    #: The upload date of the chapter.
    uploaded = models.DateTimeField(auto_now_add=True, db_index=True)
    #: The modification date of the chapter.
    modified = models.DateTimeField(auto_now=True)
    #: The groups that worked on this chapter.
    groups = models.ManyToManyField(
        Group, blank=True, related_name='releases'
    )

    class Meta:
        unique_together = ('series', 'volume', 'number')
        ordering = ('series', 'volume', 'number')
        get_latest_by = ('uploaded', 'modified')

    def save(self, *args, **kwargs):
        """Save the current instance."""
        super(Chapter, self).save(*args, **kwargs)
        if self.file:
            validators.zipfile_validator(self.file)
            Page.objects.filter(chapter=self).delete()
            self.unzip()
        self.series.completed = self.final
        self.series.save()

    @cached_property
    def next(self) -> 'Chapter':
        """Get the next chapter in the series."""
        q = Q(series_id=self.series_id) & (
            Q(volume__gt=self.volume) |
            Q(volume=self.volume, number__gt=self.number)
        )
        return self.__class__.objects.filter(q) \
            .order_by('volume', 'number').first()

    @cached_property
    def prev(self) -> 'Chapter':
        """Get the previous chapter in the series."""
        q = Q(series_id=self.series_id) & (
            Q(volume__lt=self.volume) |
            Q(volume=self.volume, number__lt=self.number)
        )
        return self.__class__.objects.filter(q) \
            .order_by('-volume', '-number').first()

    @cached_property
    def uploaded_date(self) -> str:
        """
        Get the upload date of the chapter
        in :rfc:`2616#section-3.3.1` format.
        """
        return http_date(self.uploaded.timestamp())

    @cached_property
    def modified_date(self) -> str:
        """
        Get the modification date of the chapter
        in :rfc:`2616#section-3.3.1` format.
        """
        return http_date(self.modified.timestamp())

    @cached_property
    def twitter_creator(self) -> str:
        """Get the Twitter username of the chapter's first group."""
        return '@' + Group.objects.filter(releases__id=self.id) \
            .exclude(twitter='').only('twitter').first().twitter

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`reader.views.chapter_redirect`.
        """
        return reverse('reader:chapter', args=(
            self.series.slug, self.volume, self.number
        ))

    def get_directory(self) -> str:
        """
        Get the storage directory of the object.

        :return: A path relative to
                 :const:`~MangAdventure.settings.MEDIA_ROOT`.
        """
        return self.series.get_directory() / \
            str(self.volume) / f'{self.number:g}'

    def unzip(self):
        """Unzip the chapter and save its images."""
        counter = 0
        dir_path = path.join(
            'series', self.series.slug,
            str(self.volume), f'{self.number:g}'
        )
        full_path = settings.MEDIA_ROOT / dir_path
        if path.exists(full_path):
            rmtree(full_path)
        full_path.mkdir(parents=True)
        zip_file = ZipFile(self.file)
        name_list = zip_file.namelist()
        for name in utils.natsort(name_list):
            if zip_file.getinfo(name).is_dir():
                continue
            counter += 1
            data = zip_file.read(name)
            filename = f'{counter:03d}{path.splitext(name)[-1]}'
            file_path = path.join(dir_path, filename)
            image = Image.open(BytesIO(data))
            image.save(full_path / filename, quality=100)
            self.pages.create(number=counter, image=file_path)
        zip_file.close()
        self.file.close()
        # TODO: option to keep zip file
        remove(self.file.path)
        self.file.delete(save=True)

    def zip(self) -> BytesIO:
        """
        Generate a zip file containing the pages of this chapter.

        :return: The file-like object of the generated file.
        """
        buf = BytesIO()
        with ZipFile(buf, 'a', compression=8) as zf:
            for page in self.pages.all():
                path = page.image.path
                zf.write(path, path.split('/')[-1])
        buf.seek(0)
        return buf

    @cached_property
    def _tuple(self) -> Tuple[int, int]:
        return (self.volume, self.number)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The title of the series and the
                 volume, number, title of the chapter.
        """
        return '{0.series.title} - {0.volume}/' \
               '{0.number:g}: {0.title}'.format(self)

    def __eq__(self, other: Any) -> bool:
        """
        Check whether this object is equal to another.

        If the other object is a tuple, the objects are equal if
        the tuple consists of the volume and number of the chapter.

        Otherwise, the objects are equal if they have the
        same base model and their primary keys are equal.

        :param other: Any other object.

        :return: ``True`` if the objects are equal.
        """
        if isinstance(other, tuple):
            return self._tuple == other
        return super(Chapter, self).__eq__(other)

    def __gt__(self, other: Any) -> bool:
        """
        Check whether this object is greater than another.

        If the other object is a tuple, this object is greater
        if its volume and number is greater than the tuple.

        Otherwise, it's greater if the objects have the same base model and
        the tuple of its ``volume`` and ``number`` is greater than the other's.

        :param other: Any other object.

        :return: ``True`` if this object is greater.

        :raises TypeError: If the other object is neither a tuple,
                           nor a ``Chapter`` model.
        """
        if isinstance(other, tuple):
            return self._tuple > other

        if isinstance(other, self.__class__):
            return self._tuple > other._tuple

        raise TypeError(
            "'>' not supported between instances of '{}' and '{}'"
            .format(self.__class__, other.__class__)
        )

    def __lt__(self, other):
        """
        Check whether this object is less than another.

        If the other object is a tuple, this object is lesser
        if its volume and number is less than the tuple.

        Otherwise, it's lesser if the objects have the same base model and
        the tuple of its ``volume`` and ``number`` is less than the other's.

        :param other: Any other object.

        :return: ``True`` if this object is lesser.

        :raises TypeError: If the other object is neither a tuple,
                           nor a ``Chapter`` model.
        """
        if isinstance(other, tuple):
            return self._tuple < other

        if isinstance(other, self.__class__):
            return self._tuple < other._tuple

        raise TypeError(
            "'<' not supported between instances of '{}' and '{}'"
            .format(self.__class__, other.__class__)
        )


class Page(models.Model):
    """A model representing a page."""
    #: The chapter this page belongs to.
    chapter = models.ForeignKey(
        Chapter, related_name='pages', on_delete=models.CASCADE
    )
    #: The image of the page.
    image = models.ImageField()
    #: The number of the page.
    number = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('chapter', 'number')

    @cached_property
    def _file_name(self) -> str:
        return self.image.name.split('/')[-1]

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`reader.views.chapter_page`.
        """
        return reverse('reader:page', args=(
            self.chapter.series.slug, self.chapter.volume,
            self.chapter.number, self.number
        ))

    @cached_property
    def preload(self) -> models.QuerySet:
        """
        Get the pages that will be preloaded.

        .. admonition:: TODO
           :class: warning

           Make the number of preloaded pages configurable.

        :return: The three next pages of the chapter.
        """
        return self.__class__.objects.filter(
            chapter_id=self.chapter_id,
            number__range=(self.number + 1, self.number + 3)
        ).only('image')

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The title of the series, the volume, number, title
                 of the chapter, and the file name of the page.
        """
        return '{0.series.title} - {0.volume}/{0.number} [{1}]'.format(
            self.chapter, self._file_name
        )

    def __eq__(self, other: Any) -> bool:
        """
        Check whether this object is equal to another.

        If the other object is a number, the objects are equal if
        the ``number`` of this object is equal to the other object.

        Otherwise, the objects are equal if they have the same base model
        and their ``chapter`` and ``number`` are respectively equal.

        :param other: Any other object.

        :return: ``True`` if the objects are equal.
        """
        if isinstance(other, (float, int)):
            return self.number == other

        if not isinstance(other, self.__class__):
            return False

        return self.chapter == other.chapter and self.number == other.number

    def __gt__(self, other: Any) -> bool:
        """
        Check whether this object is greater than another.

        If the other object is a number, this object is greater
        if its ``number`` is greater than the other object.

        Otherwise, it's greater if the objects have the same base model
        and the ``number`` of this object is greater than the other's.

        :param other: Any other object.

        :return: ``True`` if this object is greater.

        :raises TypeError: If the other object is neither a tuple,
                           nor a ``Page`` model.
        """
        if isinstance(other, (float, int)):
            return self.number > other

        if not isinstance(other, self.__class__):
            return self.number > other.number

        raise TypeError(
            "'>' not supported between instances of '{}' and '{}'"
            .format(self.__class__, other.__class__)
        )

    def __lt__(self, other: Any) -> bool:
        """
        Check whether this object is less than another.

        If the other object is a number, this object is lesser
        if its ``number`` is less than the other object.

        Otherwise, it's lesser if the objects have the same base model
        and the ``number`` of this object is less than the other's.

        :param other: Any other object.

        :return: ``True`` if this object is lesser.

        :raises TypeError: If the other object is neither a tuple,
                           nor a ``Page`` model.
        """
        if isinstance(other, (float, int)):
            return self.number < other

        if isinstance(other, self.__class__):
            return self.number < other.number

        raise TypeError(
            "'<' not supported between instances of '{}' and '{}'"
            .format(self.__class__, other.__class__)
        )


__all__ = [
    'Author', 'AuthorAlias', 'Artist', 'ArtistAlias',
    'Series', 'SeriesAlias', 'Chapter', 'Page', 'Category'
]

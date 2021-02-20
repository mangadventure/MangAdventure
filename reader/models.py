"""Database models for the reader app."""

from hashlib import blake2b
from io import BytesIO
from os import path, remove
from pathlib import PurePath
from shutil import rmtree
from typing import Any, List, Tuple
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.query import Q
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify

from MangAdventure import storage, utils, validators

from groups.models import Group


def _cover_uploader(obj: 'Series', name: str) -> str:
    name = f'cover.{name.split(".")[-1]}'
    name = str(obj.get_directory() / name)
    if path.exists(name):  # pragma: no cover
        remove(name)
    return name


class AliasManager(models.Manager):
    """A :class:`~django.db.models.Manager` for aliases."""
    def names(self) -> List[str]:
        """
        Get the names of the aliases.

        :return: The values of the ``alias`` field.
        """
        return list(self.get_queryset().values_list('name', flat=True))


class Alias(models.Model):
    """A generic alias :class:`~django.db.models.Model`."""
    name = models.CharField(
        blank=True, max_length=255, db_index=True, verbose_name='alias'
    )
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = AliasManager()

    class Meta:
        verbose_name_plural = 'aliases'
        unique_together = ('name', 'content_type', 'object_id')

    def __str__(self) -> str:
        """Return the alias of the instance."""
        return self.name or ''


class Author(models.Model):
    """A model representing an author."""
    #: The name of the author.
    name = models.CharField(
        max_length=100, db_index=True,
        help_text="The author's full name."
    )
    #: The aliases of the author.
    aliases = GenericRelation(
        to=Alias, blank=True, related_query_name='main'
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
    #: The aliases of the artist.
    aliases = GenericRelation(
        to=Alias, blank=True, related_query_name='main'
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
        unique=True, help_text=(
            'The name of the category. Must be '
            'unique and cannot be changed once set.'
        ), max_length=25
    )
    #: The description of the category.
    description = models.TextField(help_text='A description for the category.')

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('id',)

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
        ), upload_to=_cover_uploader,
        validators=(validators.FileSizeValidator(2),),
        storage=storage.CDNStorage((300, 300))
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
    #: The date the series was created.
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    #: The modification date of the series.
    modified = models.DateTimeField(auto_now=True)
    #: The chapter name format of the series.
    format = models.CharField(
        max_length=100, default='Vol. {volume}, Ch. {number}: {title}',
        help_text='The format used to render the chapter names.',
        verbose_name='chapter name format'
    )
    #: The aliases of the series.
    aliases = GenericRelation(
        to=Alias, blank=True, related_query_name='alias'
    )
    #: The person who manages this series.
    manager = models.ForeignKey(
        User, editable=True, blank=False, null=True,
        help_text='The person who manages this series.',
        on_delete=models.SET_NULL, limit_choices_to=(
            models.Q(is_superuser=True) | models.Q(groups__name='Scanlator')
        )
    )

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
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The title of the series.
        """
        return self.title


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
    #: The publication date of the chapter.
    published = models.DateTimeField(
        db_index=True, help_text=(
            'You can select a future date to schedule'
            ' the publication of the chapter.'
        ), default=timezone.now
    )
    #: The modification date of the chapter.
    modified = models.DateTimeField(auto_now=True)
    #: The groups that worked on this chapter.
    groups = models.ManyToManyField(
        Group, blank=True, related_name='releases'
    )

    class Meta:
        unique_together = ('series', 'volume', 'number')
        ordering = ('series', 'volume', 'number')
        get_latest_by = ('published', 'modified')

    def save(self, *args, **kwargs):
        """Save the current instance."""
        super(Chapter, self).save(*args, **kwargs)
        if self.file:
            validators.zipfile_validator(self.file)
            Page.objects.filter(chapter_id=self.id).delete()
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

    def get_directory(self) -> PurePath:
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
        pages = []
        dir_path = path.join(
            'series', self.series.slug,
            str(self.volume), f'{self.number:g}'
        )
        full_path = settings.MEDIA_ROOT / dir_path
        if full_path.exists():
            rmtree(full_path)
        full_path.mkdir(parents=True)
        with ZipFile(self.file) as zf:
            for name in utils.natsort(zf.namelist()):
                if zf.getinfo(name).is_dir():
                    continue
                counter += 1
                data = zf.read(name)
                dgst = blake2b(data, digest_size=16).hexdigest()
                filename = dgst + path.splitext(name)[-1]
                file_path = path.join(dir_path, filename)
                with open(full_path / filename, 'wb') as img:
                    img.write(data)
                pages.append(Page(
                    chapter_id=self.id, number=counter, image=file_path
                ))
        self.pages.all().delete()
        self.pages.bulk_create(pages)
        self.file.delete(save=True)

    def zip(self) -> BytesIO:
        """
        Generate a zip file containing the pages of this chapter.

        :return: The file-like object of the generated file.
        """
        buf = BytesIO()
        with ZipFile(buf, 'a', compression=8) as zf:
            for page in self.pages.iterator():
                img = page.image.path
                name = f'{page.number:03d}'
                ext = path.splitext(img)[-1]
                zf.write(img, name + ext)
        buf.seek(0)
        return buf

    @cached_property
    def _tuple(self) -> Tuple[int, float]:
        return self.volume, self.number

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The chapter formatted according to the
                 :attr:`~reader.models.Series.format`.
        """
        if not self.series:  # pragma: no cover
            return Series.format.default.format(
                title=self.title or 'N/A',
                volume=self.volume,
                number=f'{self.number:g}',
                date='', series=''
            )
        return self.series.format.format(
            title=self.title,
            volume=self.volume,
            number=f'{self.number:g}',
            date=self.published.strftime('%F'),
            series=self.series.title
        )

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
        return super().__eq__(other)

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

    def __lt__(self, other: Any) -> bool:
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

    def __hash__(self) -> int:
        """
        Return the hash of the object.

        :return: An integer hash value.
        """
        return hash(str(self)) & 0x7FFFFFFF


class _PageNumberField(models.PositiveSmallIntegerField):
    default_validators = (MinValueValidator(1),)

    def formfield(self, **kwargs):  # pragma: no cover
        # bypass parent to set min_value to 1
        return super(
            models.PositiveSmallIntegerField, self
        ).formfield(min_value=1, **kwargs)


class Page(models.Model):
    """A model representing a page."""
    #: The chapter this page belongs to.
    chapter = models.ForeignKey(
        Chapter, related_name='pages', on_delete=models.CASCADE
    )
    #: The image of the page.
    image = models.ImageField(storage=storage.CDNStorage(), max_length=255)
    #: The number of the page.
    number = _PageNumberField()

    class Meta:
        ordering = ('chapter', 'number')

    @cached_property
    def _file_name(self) -> str:
        return self.image.name.rsplit('/')[-1]

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
        return '{0.series.title} - {0.volume}/{0.number} #{1:03d}' \
            .format(self.chapter, self.number)

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

        if isinstance(other, self.__class__):
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

    def __hash__(self) -> int:
        """
        Return the hash of the object.

        :return: An integer hash value.
        """
        name = path.splitext(self._file_name)[0]
        if len(name) != 32:  # pragma: no cover
            return abs(hash(str(self)))
        return int(name, 16)


__all__ = [
    'Author', 'Artist', 'Series', 'Chapter',
    'Page', 'Category', 'Alias'
]

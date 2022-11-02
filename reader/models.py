"""
Database models for the reader app.

.. admonition:: TODO
   :class: warning

   Support multiple languages.
"""

from __future__ import annotations

from hashlib import blake2b
from importlib.util import find_spec
from io import BytesIO
from logging import getLogger
from os import path, remove
from pathlib import PurePath
from shutil import rmtree
from threading import Lock, Thread
from typing import Any, List, Tuple, Union
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.expressions import F
from django.db.models.query import Q
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.functional import cached_property
from django.utils.text import slugify

from MangAdventure import __version__ as VERSION, storage, utils, validators

from groups.models import Group

if find_spec('sentry_sdk'):  # pragma: no cover
    from sentry_sdk import capture_exception
else:
    def capture_exception(_): pass  # noqa: E704

_update_lock = Lock()
_logger = getLogger('django.db')


def _cover_uploader(obj: Series, name: str) -> str:
    name = f'cover.{name.split(".")[-1]}'
    name = str(obj.get_directory() / name)
    if path.exists(name):  # pragma: no cover
        remove(name)
    return name


class _NonZeroIntegerField(models.PositiveSmallIntegerField):
    default_validators = (MinValueValidator(1),)

    def formfield(self, **kwargs):  # pragma: no cover
        # HACK: bypass parent to set min_value to 1
        return super(
            models.PositiveSmallIntegerField, self
        ).formfield(min_value=1, **kwargs)


class AliasManager(models.Manager):
    """A :class:`~django.db.models.Manager` for aliases."""

    def names(self) -> List[str]:
        """
        Get the names of the aliases.

        :return: The values of the ``alias`` field.
        """
        qs = self.get_queryset().order_by('name')
        return list(qs.values_list('name', flat=True))


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
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'content_type', 'object_id'),
                name='unique_alias_content_object'
            ),
        )

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
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name of the category.
        """
        return self.name


class Series(models.Model):
    """
    A model representing a series.

    .. admonition:: TODO
       :class: warning

       Add age rating & reading mode fields.
    """
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
    #: The publication status of the series.
    completed = models.BooleanField(
        default=False, help_text='Is the series completed?'
    )
    #: The licensing status of the series.
    licensed = models.BooleanField(
        default=False, help_text='Is the series licensed?'
    )
    #: The date the series was created.
    created = models.DateTimeField(auto_now_add=True)
    #: The modification date of the series.
    modified = models.DateTimeField(auto_now=True, db_index=True)
    #: The chapter name format of the series.
    format = models.CharField(
        default='Vol. {volume}, Ch. {number}: {title}',
        max_length=100, verbose_name='chapter name format',
        help_text='The format used to render the chapter names.'
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
            Q(is_superuser=True) | Q(groups__name='Scanlator')
        )
    )

    class Meta:
        verbose_name_plural = 'series'
        get_latest_by = 'modified'

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

    @cached_property
    def sitemap_images(self) -> List[str]:
        """
        Get the list of images used in the sitemap.

        :return: A list containing the cover.
        """
        return [self.cover.url] if self.cover else []

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
        help_text='The number of the chapter.',
        default=0, validators=(MinValueValidator(0),)
    )
    #: The volume of the chapter.
    volume = _NonZeroIntegerField(null=True, blank=True, help_text=(
        'The volume of the chapter. Leave blank if the series has no volumes.'
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
            ' Its size cannot exceed 100 MBs and it'
            ' must not contain more than 1 subfolder.'
        ), validators=(
            validators.FileSizeValidator(100),
            validators.zipfile_validator
        ), blank=True, max_length=255
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
        ), default=tz.now
    )
    #: The modification date of the chapter.
    modified = models.DateTimeField(auto_now=True, db_index=True)
    #: The groups that worked on this chapter.
    groups = models.ManyToManyField(
        Group, blank=True, related_name='releases'
    )
    #: The total views of the chapter.
    views = models.PositiveIntegerField(
        default=0, db_index=True, editable=False,
        help_text='The total views of the chapter.'
    )

    class Meta:
        # BUG: ordering with F() seems to be broken
        # ordering = ('series', F('volume').asc(nulls_last=True), 'number')
        get_latest_by = ('published', 'modified')
        constraints = (
            models.UniqueConstraint(
                fields=('series', 'volume', 'number'),
                name='unique_chapter_number'
            ),
            models.CheckConstraint(
                check=Q(number__gte=0),
                name='chapter_number_positive'
            ),
            models.CheckConstraint(
                check=Q(volume__isnull=True) | Q(volume__gt=0),
                name='volume_number_positive'
            )
        )

    @classmethod
    def track_view(cls, **kwargs):  # pragma: no cover
        """
        Increment the chapter views in a new thread.

        :param kwargs: The arguments given to the queryset filter.
        """
        def run():
            cls.objects.filter(**kwargs).update(views=F('views') + 1)

        _update_lock.acquire()
        try:
            Thread(target=run, daemon=True, name='track_view').start()
        except Exception as exc:
            _logger.exception(exc)
            capture_exception(exc)
        finally:
            _update_lock.release()

    def save(self, *args, **kwargs):
        """Save the current instance."""
        super().save(*args, **kwargs)
        if self.file:
            validators.zipfile_validator(self.file)
            self.unzip()
        self.series.completed = self.final
        self.series.save(update_fields=('completed',))

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`reader.views.chapter_redirect`.
        """
        return reverse('reader:chapter', args=(
            self.series.slug, self.volume or 0, self.number
        ))

    def get_directory(self) -> PurePath:
        """
        Get the storage directory of the object.

        :return: A path relative to
                 :const:`~MangAdventure.settings.MEDIA_ROOT`.
        """
        return self.series.get_directory() / \
            str(self.volume or 0) / f'{self.number:g}'

    def unzip(self):
        """Unzip the chapter and save its images."""
        counter = 0
        pages = []
        dir_path = path.join(
            'series', self.series.slug,
            str(self.volume or 0), f'{self.number:g}'
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
                (full_path / filename).write_bytes(data)
                pages.append(Page(
                    chapter_id=self.id, number=counter, image=file_path
                ))
        self.pages.all().delete()
        self.pages.bulk_create(pages)
        self.file.delete(save=True)
        cache.delete(f'chapter.cbz.{self.id}')

    def zip(self) -> BytesIO:
        """
        Generate a zip file containing the pages of this chapter.

        :return: The file-like object of the generated file.
        """
        buf = cache.get(f'chapter.cbz.{self.id}', BytesIO())
        if not buf.getvalue():
            info = self.comicinfo()
            pages = ET.SubElement(info, 'Pages')

            with ZipFile(buf, 'a', compression=8) as zf:
                for page in self.pages.all():
                    img = page.image.path
                    name = f'{page.number:03d}'
                    ext = path.splitext(img)[-1]
                    zf.write(img, name + ext)

                    ET.SubElement(pages, 'Page', {
                        'Image': str(page.number),
                        'ImageSize': str(page.image.size),
                        'ImageWidth': str(page.image.width),
                        'ImageHeight': str(page.image.height)
                    })

                zf.writestr('ComicInfo.xml', ET.tostring(
                    info, encoding='UTF-8', xml_declaration=True
                ))
            buf.seek(0)
            cache.add(f'chapter.cbz.{self.id}', buf)
        return buf

    def comicinfo(self) -> ET.Element:
        """
        Generate an XML file containing the chapter's metadata.

        :return: The root XML element.

        .. seealso::

            https://anansi-project.github.io/docs/comicinfo/documentation
        """
        root = ET.Element('ComicInfo', {
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation':
                'https://raw.githubusercontent.com/anansi-project'
                '/comicinfo/main/drafts/v2.1/ComicInfo.xsd'
        })

        title = ET.SubElement(root, 'Title')
        title.text = str(self)

        series = ET.SubElement(root, 'Series')
        series.text = str(self.series)

        number = ET.SubElement(root, 'Number')
        number.text = str(self.number)

        volume = ET.SubElement(root, 'Volume')
        volume.text = str(self.volume)

        notes = ET.SubElement(root, 'Notes')
        notes.text = f'Created by MangAdventure v{VERSION}'

        published = self.published.timetuple()
        year = ET.SubElement(root, 'Year')
        year.text = str(published.tm_year)
        month = ET.SubElement(root, 'Month')
        month.text = str(published.tm_mon)
        day = ET.SubElement(root, 'Day')
        day.text = str(published.tm_mday)

        writer = ET.SubElement(root, 'Writer')
        writer.text = ', '.join(a.name for a in self.series.authors.all())

        penciller = ET.SubElement(root, 'Penciller')
        penciller.text = ', '.join(a.name for a in self.series.artists.all())

        translator = ET.SubElement(root, 'Translator')
        translator.text = ', '.join(g.name for g in self.groups.all())

        genre = ET.SubElement(root, 'Genre')
        genre.text = ', '.join(c.name for c in self.series.categories.all())

        domain = settings.CONFIG['DOMAIN']
        scheme = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        web = ET.SubElement(root, 'Web')
        web.text = f'{scheme}://{domain}{self.get_absolute_url()}'

        count = ET.SubElement(root, 'PageCount')
        count.text = str(len(self.pages.all()))

        language = ET.SubElement(root, 'LanguageISO')
        language.text = 'en'

        manga = ET.SubElement(root, 'Manga')
        manga.text = 'Yes'

        return root

    @cached_property
    def sitemap_images(self) -> List[str]:
        """
        Get the list of images used in the sitemap.

        :return: A list containing the pages.
        """
        return [p.image.url for p in self.pages.all()]

    @cached_property
    def _tuple(self) -> Tuple[Union[int, float], float]:
        return self.volume or float('inf'), self.number

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The chapter formatted according to the
                 :attr:`~reader.models.Series.format`.
        """
        # TODO: use removeprefix (Py3.9+)
        if not self.series:  # pragma: no cover
            return Series.format.default.format(
                title=self.title or 'N/A',
                volume=self.volume or '?',
                number=f'{self.number:g}',
                date='', series=''
            ).replace('Vol. ?, ', '')
        return self.series.format.format(
            title=self.title,
            volume=self.volume or '?',
            number=f'{self.number:g}',
            date=self.published.strftime('%F'),
            series=self.series.title
        ).replace('Vol. ?, ', '')

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
            "'>' not supported between instances of " +
            f"'{self.__class__}' and '{other.__class__}'"
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
            "'<' not supported between instances of " +
            f"'{self.__class__}' and '{other.__class__}'"
        )

    def __hash__(self) -> int:
        """
        Return the hash of the object.

        :return: An integer hash value.
        """
        return hash(str(self)) & 0x7FFFFFFF


class Page(models.Model):
    """
    A model representing a page.

    .. admonition:: TODO
       :class: warning

       Add page type, double page, width/height fields.
    """
    #: The chapter this page belongs to.
    chapter = models.ForeignKey(
        Chapter, related_name='pages', on_delete=models.CASCADE
    )
    #: The image of the page.
    image = models.ImageField(storage=storage.CDNStorage(), max_length=255)
    #: The number of the page.
    number = _NonZeroIntegerField()

    class Meta:
        ordering = ('chapter', 'number')
        constraints = (
            models.CheckConstraint(
                check=Q(number__gte=1),
                name='page_number_nonzero'
            ),
        )

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`reader.views.chapter_page`.
        """
        return reverse('reader:page', args=(
            self.chapter.series.slug,
            self.chapter.volume or 0,
            self.chapter.number, self.number
        ))

    @cached_property
    def _thumb(self) -> models.ImageField:
        img = self.image
        img.storage = storage.CDNStorage((150, 150))
        return img

    @cached_property
    def _file_name(self) -> str:
        return self.image.name.rsplit('/')[-1]

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
            "'<' not supported between instances of " +
            f"'{self.__class__}' and '{other.__class__}'"
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
            "'<' not supported between instances of " +
            f"'{self.__class__}' and '{other.__class__}'"
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
    'Author', 'Artist', 'Series',
    'Chapter', 'Page', 'Category', 'Alias'
]

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from django.conf import settings
from django.db import models
from MangAdventure.modules.alias import Alias, alias_field, foreign_key
from MangAdventure.modules.uploaders import cover_uploader
from MangAdventure.modules.storage import OverwriteStorage
from MangAdventure.modules.sort import natural_sort
from MangAdventure.modules.validators import *
from groups.models import Group
from os import path, remove, makedirs
from zipfile import ZipFile
from sys import getsizeof
from io import BytesIO
from PIL import Image


class Author(models.Model):
    name = models.CharField(max_length=100,
                            help_text="The author's full name.")

    def delete(self, using=None, keep_parents=False):
        Series.authors.through.objects.filter(author=self).delete()
        super(Author, self).delete(using, keep_parents)

    def __str__(self): return self.name


class Artist(models.Model):
    name = models.CharField(max_length=100,
                            help_text="The artist's full name.")

    def delete(self, using=None, keep_parents=False):
        Series.artists.through.objects.filter(artist=self).delete()
        super(Artist, self).delete(using, keep_parents)

    def __str__(self): return self.name


class Series(models.Model):
    title = models.CharField(max_length=250,
                             help_text='The title of the series.')
    description = models.TextField(blank=True,
                                   help_text='The description of the series.')
    cover = models.ImageField(storage=OverwriteStorage(),
                              upload_to=cover_uploader,
                              help_text='Upload a cover image for the series.'
                                        ' Its size must not exceed 2 MBs.',
                              validators=[FileSizeValidator(max_mb=2)])
    authors = models.ManyToManyField(Author, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    slug = models.SlugField(primary_key=True, blank=True,
                            verbose_name='Custom URL',
                            help_text='A custom URL for the series. Must be '
                                      'unique and cannot be changed once set.')
    completed = models.BooleanField(default=False,
                                    help_text='Is the series completed?')
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'series'
        get_latest_by = 'modified'

    def save(self, *args, **kwargs):
        self.validate_unique()
        self.slug = self.slug or slugify(self.title)
        img = Image.open(self.cover)
        img.thumbnail((300, 300), Image.ANTIALIAS)
        Image.MIME['ICO'] = 'image/x-icon'
        mime = Image.MIME.get(img.format)
        buff = BytesIO()
        img.save(buff, format=img.format, quality=100)
        buff.seek(0)
        self.cover = InMemoryUploadedFile(buff, 'ImageField',
                                          self.cover.name, mime,
                                          getsizeof(buff), None)
        super(Series, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.authors.clear()
        self.artists.clear()
        super(Series, self).delete(using, keep_parents)

    def __str__(self): return self.title


class AuthorAlias(Alias):
    author = foreign_key(Author)
    alias = alias_field('Another name for the author.')


class ArtistAlias(Alias):
    artist = foreign_key(Artist)
    alias = alias_field('Another name for the artist.')


class SeriesAlias(Alias):
    series = foreign_key(Series)
    alias = alias_field('Another title for the series.', 250)


class Chapter(models.Model):
    _help = 'The %s of the chapter.'
    _vol_help = _help % 'volume' + ' Leave as 0 if the series has no volumes.'
    _file_help = [
        'Upload a zip or cbz file containing the chapter pages.',
        'Its size cannot exceed 50 MBs and it must not',
        'contain more than 1 subfolder.'
    ]
    title = models.CharField(max_length=250, help_text=_help % 'title')
    number = models.PositiveSmallIntegerField(default=0,
                                              help_text=_help % 'number')
    volume = models.PositiveSmallIntegerField(default=0, help_text=_vol_help)
    series = models.ForeignKey(Series, on_delete=models.CASCADE,
                               related_name='chapters',
                               help_text='The series this chapter belongs to.')
    file = models.FileField(help_text=' '.join(_file_help),
                            blank=True, validators=[
                                FileSizeValidator(max_mb=50),
                                validate_zip_file])
    final = models.BooleanField(default=False,
                                help_text='Is this the final chapter?')
    url = models.FilePathField(auto_created=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(Group, blank=True, related_name='releases')

    class Meta:
        unique_together = ('series', 'volume', 'number')
        ordering = ('series', 'volume', 'number')
        get_latest_by = ('uploaded', 'modified')

    def save(self, *args, **kwargs):
        self.url = '/reader/%s/%d/%d/' % (self.series.slug,
                                          self.volume, self.number)
        super(Chapter, self).save(*args, **kwargs)
        if self.file:
            validate_zip_file(self.file)
            counter = 0
            zip_file = ZipFile(self.file)
            name_list = zip_file.namelist()
            Page.objects.filter(chapter=self).delete()
            for name in natural_sort(name_list):
                if is_dir(zip_file.getinfo(name)):
                    continue
                counter += 1
                data = zip_file.read(name)
                filename = '%03d%s' % (counter, path.splitext(name)[-1])
                file_path = path.join(
                    'series',
                    self.series.slug,
                    str(self.volume),
                    str(self.number),
                    filename
                )
                full_path = path.join(settings.MEDIA_ROOT, file_path)
                if not path.exists(path.dirname(full_path)):
                    makedirs(path.dirname(full_path))
                if path.exists(full_path):
                    remove(full_path)
                image = Image.open(BytesIO(data))
                image.save(full_path, optimize=True, quality=100)
                self.pages.create(number=counter, image=file_path)
            zip_file.close()
            remove(self.file.path)
            self.file.delete(save=True)
        self.series.completed = self.final
        self.series.save()

    def __str__(self):
        return '%s - %d/%d: %s' % \
               (self.series, self.volume,
                self.number, self.title)


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='pages',
                                on_delete=models.CASCADE)
    image = models.ImageField()
    number = models.PositiveSmallIntegerField()


__all__ = [
    'Author', 'AuthorAlias', 'Artist', 'ArtistAlias',
    'Series', 'SeriesAlias', 'Chapter', 'Page'
]


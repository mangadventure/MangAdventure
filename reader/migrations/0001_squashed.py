from datetime import datetime
from os import path, rename

from django.db import migrations, models
from django.utils import timezone

from MangAdventure import storage, validators
from MangAdventure.models import AliasField, AliasKeyField

from reader.models import _cover_uploader


def hash_pages(apps, schema_editor):
    from hashlib import shake_128
    Page = apps.get_model('reader', 'Page')
    for page in Page.objects.all():
        old_path = page.image.path
        with open(old_path, 'rb') as img:
            sha = shake_128(img.read()).hexdigest(16)
        name, ext = path.splitext(old_path)
        parent = path.split(name)[0]
        page.image.name = path.join(parent, sha + ext)
        rename(old_path, page.image.path)
        page.image.save(page.image.name, page.image)


def counter_pages(apps, schema_editor):
    Page = apps.get_model('reader', 'Page')
    for page in Page.objects.all():
        old_path = page.image.path
        cnt = f'{page.number:03d}'
        name, ext = path.splitext(page.image.name)
        parent = path.split(name)[0]
        page.image.name = path.join(parent, cnt + ext)
        rename(old_path, page.image.path)
        page.image.save(page.image.name, page.image)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('groups', '0001_initial'),
    ]

    # TODO: remove squashed migrations after application
    replaces = [
        ('reader', '0001_initial'),
        ('reader', '0002_reader_dates'),
        ('reader', '0003_chapter_groups'),
        ('reader', '0004_float_numbers'),
        ('reader', '0005_categories'),
        ('reader', '0006_remove_chapter_url'),
        ('reader', '0007_editable_slugs'),
        ('reader', '0008_add_indexes'),
        ('reader', '0009_cdn_storage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('name', models.CharField(
                    help_text="The artist's full name.",
                    max_length=100, db_index=True
                )),
            ],
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('alias', AliasField(
                    blank=True, help_text='Another name for the artist.',
                    max_length=100, unique=True, db_index=True
                )),
                ('artist', AliasKeyField(
                    on_delete=models.deletion.CASCADE,
                    related_name='aliases', to='reader.Artist'
                )),
            ],
            options={
                'verbose_name': 'alias',
                'verbose_name_plural': 'aliases',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('name', models.CharField(
                    help_text="The author's full name.",
                    max_length=100, db_index=True
                )),
            ],
        ),
        migrations.CreateModel(
            name='AuthorAlias',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('alias', AliasField(
                    blank=True, help_text='Another name for the author.',
                    max_length=100, unique=True, db_index=True
                )),
                ('author', AliasKeyField(
                    on_delete=models.deletion.CASCADE,
                    related_name='aliases', to='reader.Author'
                )),
            ],
            options={
                'verbose_name': 'alias',
                'verbose_name_plural': 'aliases',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('title', models.CharField(
                    help_text='The title of the chapter.', max_length=250
                )),
                ('number', models.FloatField(
                    default=0, help_text='The number of the chapter.'
                )),
                ('volume', models.PositiveSmallIntegerField(
                    default=0, help_text=(
                        'The volume of the chapter. Leave '
                        'as 0 if the series has no volumes.'
                    )
                )),
                ('file', models.FileField(
                    blank=True, help_text=(
                        'Upload a zip or cbz file containing the '
                        'chapter pages. Its size cannot exceed 50 MBs '
                        'and it must not contain more than 1 subfolder.'
                    ), upload_to='', validators=(
                        validators.FileSizeValidator(50),
                        validators.zipfile_validator
                    )
                )),
                ('final', models.BooleanField(
                    default=False, help_text='Is this the final chapter?'
                )),
                ('modified', models.DateTimeField(
                    default=datetime.now(tz=timezone.utc)
                )),
                ('uploaded', models.DateTimeField(
                    default=datetime.now(tz=timezone.utc)
                )),
            ],
            options={
                'get_latest_by': ('uploaded', 'modified'),
                'ordering': ('series', 'volume', 'number'),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('image', models.ImageField(
                    storage=storage.CDNStorage(), upload_to=''
                )),
                ('number', models.PositiveSmallIntegerField()),
                ('chapter', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='pages', to='reader.Chapter'
                )),
            ],
            options={
                'ordering': ('chapter', 'number')
            },
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('title', models.CharField(
                    help_text='The title of the series.',
                    max_length=250, db_index=True
                )),
                ('description', models.TextField(
                    blank=True, help_text='The description of the series.'
                )),
                ('cover', models.ImageField(
                    help_text=(
                        'Upload a cover image for the series.'
                        ' Its size must not exceed 2 MBs.'
                    ), upload_to=_cover_uploader,
                    storage=storage.CDNStorage((300, 300)),
                    validators=(validators.FileSizeValidator(2),)
                )),
                ('slug', models.SlugField(
                    primary_key=False, unique=True,
                    blank=True, help_text=(
                        'The unique slug of the series.'
                        ' Will be used in the URL.'
                    ), verbose_name='Custom slug',
                )),
                ('completed', models.BooleanField(
                    default=False, help_text='Is the series completed?'
                )),
                ('artists', models.ManyToManyField(
                    blank=True, to='reader.Artist'
                )),
                ('authors', models.ManyToManyField(
                    blank=True, to='reader.Author'
                )),
                ('modified', models.DateTimeField(
                    default=datetime.now(tz=timezone.utc)
                )),
            ],
            options={
                'get_latest_by': 'modified',
                'verbose_name_plural': 'series',
            },
        ),
        migrations.CreateModel(
            name='SeriesAlias',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('alias', AliasField(
                    blank=True, help_text='Another title for the series.',
                    max_length=250, unique=True, db_index=True
                )),
                ('series', AliasKeyField(
                    on_delete=models.deletion.CASCADE,
                    related_name='aliases', to='reader.Series'
                )),
            ],
            options={
                'verbose_name': 'alias',
                'verbose_name_plural': 'aliases',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.CharField(
                    auto_created=True, primary_key=True,
                    max_length=25, serialize=False, default=''
                )),
                ('name', models.CharField(
                    max_length=25, help_text=(
                        'The name of the category. Must be '
                        'unique and cannot be changed once set.'
                    ), unique=True
                )),
                ('description', models.TextField(
                    help_text='A description for the category.'
                )),
            ],
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AddField(
            model_name='chapter',
            name='series',
            field=models.ForeignKey(
                help_text='The series this chapter belongs to.',
                on_delete=models.deletion.CASCADE,
                related_name='chapters', to='reader.Series'
            ),
        ),
        migrations.AddField(
            model_name='chapter',
            name='groups',
            field=models.ManyToManyField(
                blank=True, related_name='releases', to='groups.Group'
            ),
        ),
        migrations.AddField(
            model_name='series',
            name='categories',
            field=models.ManyToManyField(
                blank=True, to='reader.Category'
            ),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='uploaded',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='series',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='chapter',
            unique_together={('series', 'volume', 'number')},
        ),
        # TODO: remove renaming operation after application
        migrations.RunPython(hash_pages, counter_pages),
    ]

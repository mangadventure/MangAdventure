from datetime import datetime, timezone

from django.db import migrations, models

from MangAdventure import storage, validators

from reader.models import _cover_uploader, _NonZeroIntegerField


class Migration(migrations.Migration):
    initial = True

    dependencies = [('groups', '0001_squashed')]

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
                ('alias', models.CharField(
                    blank=True, help_text='Another name for the artist.',
                    max_length=100, unique=True, db_index=True
                )),
                ('artist', models.ForeignKey(
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
                ('alias', models.CharField(
                    blank=True, help_text='Another name for the author.',
                    max_length=100, unique=True, db_index=True
                )),
                ('author', models.ForeignKey(
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
                    storage=storage.CDNStorage(),
                    upload_to='', max_length=255
                )),
                ('number', _NonZeroIntegerField()),
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
                ('alias', models.CharField(
                    blank=True, help_text='Another title for the series.',
                    max_length=250, unique=True, db_index=True
                )),
                ('series', models.ForeignKey(
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
    ]

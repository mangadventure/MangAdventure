import datetime
from django.db import migrations, models
import django.db.models.deletion
import MangAdventure.models
import MangAdventure.utils.storage
import MangAdventure.utils.uploaders
import MangAdventure.utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="The artist's full name.", max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', MangAdventure.models.AliasField(blank=True, help_text='Another name for the artist.', max_length=100, unique=True)),
                ('artist', MangAdventure.models.AliasKeyField(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='reader.Artist')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="The author's full name.", max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AuthorAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', MangAdventure.models.AliasField(blank=True, help_text='Another name for the author.', max_length=100, unique=True)),
                ('author', MangAdventure.models.AliasKeyField(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='reader.Author')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.FilePathField(auto_created=True)),
                ('title', models.CharField(help_text='The title of the chapter.', max_length=250)),
                ('number', models.PositiveSmallIntegerField(default=0, help_text='The number of the chapter. ')),
                ('volume', models.PositiveSmallIntegerField(default=0, help_text='The volume of the chapter. Leave as 0 if the series has no volumes.')),
                ('date', models.DateField(default=datetime.date.today, help_text='The date the chapter was uploaded. You may choose a past date.')),
                ('file', models.FileField(help_text='Upload a zip or cbz file containing the chapter pages. Its size cannot exceed 50 MBs and it must not contain more than 1 subfolder.', upload_to='', validators=[
                    MangAdventure.utils.validators.FileSizeValidator(max_mb=50), MangAdventure.utils.validators.zipfile_validator])),
                ('final', models.BooleanField(default=False, help_text='Is this the final chapter?')),
            ],
            options={
                'ordering': ('series', 'volume', 'number'),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('number', models.PositiveSmallIntegerField()),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='reader.Chapter')),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('title', models.CharField(help_text='The title of the series.', max_length=250)),
                ('description', models.TextField(blank=True, help_text='The description of the series.')),
                ('cover', models.ImageField(help_text='Upload a cover image for the series. Its size must not exceed 2 MBs.', storage=MangAdventure.utils.storage.OverwriteStorage(), upload_to=MangAdventure.utils.uploaders.cover_uploader, validators=[
                    MangAdventure.utils.validators.FileSizeValidator(max_mb=2)])),
                ('slug', models.SlugField(blank=True, help_text='A custom URL for the series. Must be unique and cannot be changed once set.', primary_key=True, serialize=False, verbose_name='Custom URL')),
                ('completed', models.BooleanField(default=False, help_text='Is the series completed?')),
                ('artists', models.ManyToManyField(blank=True, to='reader.Artist')),
                ('authors', models.ManyToManyField(blank=True, to='reader.Author')),
            ],
            options={
                'verbose_name_plural': 'series',
            },
        ),
        migrations.CreateModel(
            name='SeriesAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', MangAdventure.models.AliasField(blank=True, help_text='Another title for the series.', max_length=250, unique=True)),
                ('series', MangAdventure.models.AliasKeyField(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='reader.Series')),
            ],
            options={
                'verbose_name': 'alias',
                'verbose_name_plural': 'aliases',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='chapter',
            name='series',
            field=models.ForeignKey(help_text='The series this chapter belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='reader.Series'),
        ),
        migrations.AlterUniqueTogether(
            name='chapter',
            unique_together={('series', 'volume', 'number')},
        ),
    ]

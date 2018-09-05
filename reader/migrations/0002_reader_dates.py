from django.utils import timezone
from django.db import migrations, models
from datetime import datetime
from MangAdventure.modules import validators


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'get_latest_by': ('uploaded', 'modified'), 'ordering': ('series', 'volume', 'number')},
        ),
        migrations.AlterModelOptions(
            name='series',
            options={'get_latest_by': 'modified', 'verbose_name_plural': 'series'},
        ),
        migrations.RemoveField(
            model_name='chapter',
            name='date',
        ),
        migrations.AddField(
            model_name='chapter',
            name='modified',
            field=models.DateTimeField(default=datetime.now(tz=timezone.utc)),
        ),
        migrations.AddField(
            model_name='chapter',
            name='uploaded',
            field=models.DateTimeField(default=datetime.now(tz=timezone.utc)),
        ),
        migrations.AddField(
            model_name='series',
            name='modified',
            field=models.DateTimeField(default=datetime.now(tz=timezone.utc)),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='uploaded',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='series',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='file',
            field=models.FileField(blank=True,
                                   help_text='Upload a zip or cbz file containing the chapter pages. Its size cannot exceed 50 MBs and it must not contain more than 1 subfolder.',
                                   upload_to='', validators=[validators.FileSizeValidator(max_mb=50),
                                                             validators.validate_zip_file]),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='number',
            field=models.PositiveSmallIntegerField(default=0, help_text='The number of the chapter.'),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='volume',
            field=models.PositiveSmallIntegerField(default=0, help_text='The volume of the chapter. Leave as 0 if the series has no volumes.'),
        ),
    ]

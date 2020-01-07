from django.db import migrations, models

from MangAdventure.storage import CDNStorage
from MangAdventure.validators import FileSizeValidator, zipfile_validator

import reader.models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0008_add_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='file',
            field=models.FileField(
                blank=True, help_text=(
                    'Upload a zip or cbz file containing the '
                    'chapter pages. Its size cannot exceed 50 MBs '
                    'and it must not contain more than 1 subfolder.'
                ), upload_to='', validators=[
                    FileSizeValidator(50), zipfile_validator
                ])
        ),
        migrations.AlterField(
            model_name='page',
            name='image',
            field=models.ImageField(
                storage=CDNStorage(), upload_to='', max_length=255
            )
        ),
        migrations.AlterField(
            model_name='series',
            name='cover',
            field=models.ImageField(
                help_text=(
                    'Upload a cover image for the series.'
                    ' Its size must not exceed 2 MBs.'
                ), storage=CDNStorage((300, 300)),
                upload_to=reader.models._cover_uploader,
                validators=[FileSizeValidator(2)])
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(help_text='A description for the category.')
        )
    ]

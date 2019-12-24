from os import path, rename

from django.db import migrations, models

from MangAdventure.storage import CDNStorage
from MangAdventure.validators import FileSizeValidator, zipfile_validator

import reader.models


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
            field=models.ImageField(storage=CDNStorage(), upload_to='')
        ),
        migrations.RunPython(hash_pages, counter_pages),
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
        )
    ]

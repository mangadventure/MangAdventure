from django.db import migrations, models

from MangAdventure import validators


class Migration(migrations.Migration):
    dependencies = [('reader', '0005_managers')]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='file',
            field=models.FileField(
                blank=True, help_text=(
                    'Upload a zip or cbz file containing the '
                    'chapter pages. Its size cannot exceed 50 MBs '
                    'and it must not contain more than 1 subfolder.'
                ), upload_to='', validators=(
                    validators.FileSizeValidator(50),
                    validators.zipfile_validator
                ), max_length=255
            )
        ),
    ]

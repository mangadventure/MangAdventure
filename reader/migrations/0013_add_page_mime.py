from django.db import migrations, models

from MangAdventure.validators import FileSizeValidator


class Migration(migrations.Migration):
    dependencies = [
        ('reader', '0012_more_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={
                'get_latest_by': ('published', 'modified'),
                'ordering': (
                    'series',
                    models.OrderBy(models.F('volume'), nulls_last=True),
                    'number'
                )
            }
        ),
        migrations.AddField(
            model_name='page',
            name='mime',
            field=models.CharField(
                editable=False, max_length=25, default='image/jpeg'
            ),
            preserve_default=False
        ),
        migrations.AlterField(
            model_name='chapter',
            name='file',
            field=models.FileField(
                blank=True, help_text=(
                    'Upload a zip or cbz file containing the '
                    'chapter pages. Its size cannot exceed 100 MBs '
                    'and it must not contain more than 1 subfolder.'
                ), upload_to='', validators=(
                    FileSizeValidator(100),
                ), max_length=255
            )
        ),
    ]

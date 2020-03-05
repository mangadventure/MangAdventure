from django.db import migrations, models
from django.utils import timezone as tz


class Migration(migrations.Migration):
    dependencies = [
        ('reader', '0002_series_created'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={
                'get_latest_by': ('published', 'modified'),
                'ordering': ('series', 'volume', 'number')
            },
        ),
        migrations.RenameField(
            model_name='chapter',
            old_name='uploaded',
            new_name='published',
        ),
        migrations.AlterField(
            model_name='chapter',
            name='published',
            field=models.DateTimeField(
                auto_now_add=False, default=tz.now,
                db_index=True, help_text=(
                    'You can select a future date to schedule'
                    ' the publication of the chapter.'
                )
            ),
        )
    ]

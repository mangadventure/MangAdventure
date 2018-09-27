from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reader', '0003_chapter_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='number',
            field=models.FloatField(default=0, help_text='The number of the chapter.'),
        ),
    ]


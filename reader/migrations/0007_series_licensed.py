from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('reader', '0006_file_limits')]

    operations = [
        migrations.AddField(
            model_name='series',
            name='licensed',
            field=models.BooleanField(
                default=False, help_text='Is the series licensed?'
            ),
        ),
    ]

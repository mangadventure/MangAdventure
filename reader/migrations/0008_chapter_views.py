from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('reader', '0007_series_licensed')]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='views',
            field=models.PositiveIntegerField(
                db_index=True, default=0, editable=False,
                help_text='The total views of the chapter.'
            ),
        ),
    ]

from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [('reader', '0011_series_status')]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.CharField(
                auto_created=True, db_default=models.Value(''),
                max_length=25, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='views',
            field=models.PositiveIntegerField(
                db_default=models.Value(0), db_index=True,
                editable=False, help_text='The total views of the chapter.'
            ),
        ),
    ]

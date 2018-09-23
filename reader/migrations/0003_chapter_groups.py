from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
        ('reader', '0002_reader_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='releases',
                                         to='groups.Group'),
        ),
    ]


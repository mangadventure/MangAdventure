from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_cdn_storage'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='groups',
            field=models.ManyToManyField(
                blank=False, related_name='members',
                through='groups.Role', to='groups.Group'
            )
        )
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('users', '0003_apikey')]

    operations = [
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='bookmark',
            constraint=models.UniqueConstraint(
                fields=('series', 'user'),
                name='unique_bookmark'
            ),
        ),
    ]

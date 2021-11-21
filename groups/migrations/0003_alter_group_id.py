from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('groups', '0002_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='id',
            field=models.SmallAutoField(
                auto_created=True, primary_key=True,
                serialize=False, verbose_name='ID'
            ),
        ),
    ]

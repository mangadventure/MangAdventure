from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reader', '0004_aliases'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='manager',
            field=models.ForeignKey(
                help_text='The person who manages this series.',
                blank=False, null=True, on_delete=models.SET_NULL,
                to=settings.AUTH_USER_MODEL, limit_choices_to=models.Q(
                    ('is_superuser', True),
                    ('groups__name', 'Scanlator'),
                    _connector='OR'
                ),
            ),
        ),
    ]

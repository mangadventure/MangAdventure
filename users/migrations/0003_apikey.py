from secrets import token_hex

from django.conf import settings
from django.db import migrations, models


def populate_keys(apps, schema_editor):
    user = apps.get_model('auth', 'User')
    api_key = apps.get_model('users', 'ApiKey')
    api_key.objects.bulk_create(
        api_key(user_id=uid) for uid in
        user.objects.values_list('id', flat=True)
    )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_userprofile_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('key', models.CharField(
                    primary_key=True, max_length=64,
                    serialize=False, default=token_hex
                )),
                ('user', models.OneToOneField(
                    on_delete=models.deletion.CASCADE, unique=True,
                    related_name='api_key', to=settings.AUTH_USER_MODEL
                )),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RunPython(populate_keys, migrations.RunPython.noop)
    ]

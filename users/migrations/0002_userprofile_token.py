from hmac import new as digest

from django.conf import settings
from django.db import migrations, models


def populate_tokens(apps, schema_editor):
    user_profile = apps.get_model('users', 'UserProfile')
    profiles = user_profile.objects.all()
    for p in profiles:
        data = f'{p.user.username}:{p.user.password}'
        p.token = digest(
            settings.SECRET_KEY.encode(),
            data.encode(), 'shake128'
        ).hexdigest()
    user_profile.objects.bulk_update(profiles, ('token',))


class Migration(migrations.Migration):
    dependencies = [('users', '0001_squashed')]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='token',
            field=models.CharField(
                auto_created=True, blank=True, null=True,
                editable=False, unique=False, max_length=32
            )
        ),
        migrations.RunPython(populate_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userprofile',
            name='token',
            field=models.CharField(
                auto_created=True, blank=False, null=False,
                editable=False, unique=True, max_length=32
            )
        )
    ]

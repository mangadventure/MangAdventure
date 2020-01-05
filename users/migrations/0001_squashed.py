from django.conf import settings
from django.db import migrations, models

from MangAdventure import storage, validators

from users.models import _avatar_uploader


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reader', '0001_initial'),
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    # TODO: remove squashed migrations after application
    replaces = [
        ('users', '0001_initial'),
        ('users', '0002_progress_userprofile'),
        ('users', '0002_userprofile'),
        ('users', '0003_cdn_storage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('series', models.ForeignKey(
                    on_delete=models.deletion.CASCADE, to='reader.Series'
                )),
                ('user', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='bookmarks', to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('bio', models.TextField(
                    blank=True, verbose_name='biography',
                    help_text="The user's biography."
                )),
                ('avatar', models.ImageField(
                    blank=True, help_text=(
                        "The user's avatar image. Must be up to 2 MBs."
                    ), upload_to=_avatar_uploader,
                    storage=storage.CDNStorage((150, 150)),
                    validators=(validators.FileSizeValidator(2),)
                )),
                ('user', models.OneToOneField(
                    on_delete=models.deletion.CASCADE,
                    related_name='profile', to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together={('series', 'user')},
        ),
    ]

from django.conf import settings
from django.db import migrations, models

from MangAdventure.utils import storage, validators

from users.models import _avatar_uploader


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('reader', '0006_remove_chapter_url'),
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('chapter', models.ForeignKey(
                    on_delete=models.deletion.CASCADE, to='reader.Chapter'
                )),
                ('user', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='progress', to=settings.AUTH_USER_MODEL
                )),
                ('last_update', models.DateTimeField(auto_now=True))
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
                    blank=True, help_text="The user's biography.",
                    verbose_name='biography'
                )),
                ('avatar', models.ImageField(
                    blank=True, help_text="The user's avatar image."
                    " Must be up to 2 MBs.",
                    storage=storage.OverwriteStorage(),
                    upload_to=_avatar_uploader,
                    validators=(validators.FileSizeValidator(max_mb=2),)
                )),
                ('bookmarks', models.ManyToManyField(
                    blank=True, help_text="The user's bookmarked series.",
                    related_name='profile', to='users.Bookmark'
                )),
                ('user', models.OneToOneField(
                    on_delete=models.deletion.CASCADE,
                    related_name='profile', to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
    ]

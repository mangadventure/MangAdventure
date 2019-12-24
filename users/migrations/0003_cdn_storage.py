from django.db import migrations, models

from MangAdventure.storage import CDNStorage
from MangAdventure.validators import FileSizeValidator

import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(
                blank=True, help_text=(
                    "The user's avatar image. Must be up to 2 MBs."
                ), storage=CDNStorage((150, 150)),
                upload_to=users.models._avatar_uploader,
                validators=[FileSizeValidator(2)])
        )
    ]

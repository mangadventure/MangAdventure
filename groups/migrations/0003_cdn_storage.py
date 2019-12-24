from django.db import migrations, models

from MangAdventure.storage import CDNStorage
from MangAdventure.validators import FileSizeValidator

import groups.models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_irc_reddit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='logo',
            field=models.ImageField(
                blank=True, help_text=(
                    "Upload the group's logo. Its size must not exceed 2 MBs."
                ), storage=CDNStorage((150, 150)),
                upload_to=groups.models._logo_uploader,
                validators=[FileSizeValidator(2)]
            )
        )
    ]

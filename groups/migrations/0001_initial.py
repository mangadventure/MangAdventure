from django.db import migrations, models

from MangAdventure.models import DiscordNameField, DiscordURLField, TwitterField
from MangAdventure.utils import storage, uploaders, validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.SmallIntegerField(
                    auto_created=True, primary_key=True, serialize=False
                )),
                ('name', models.CharField(
                    help_text="The group's name.", max_length=100
                )),
                ('website', models.URLField(help_text="The group's website.")),
                ('email', models.EmailField(
                    blank=True, max_length=254,
                    help_text="The group's E-mail address."
                )),
                ('discord', DiscordURLField(
                    blank=True, help_text="The group's Discord link."
                )),
                ('twitter', TwitterField(
                    blank=True, max_length=15,
                    help_text="The group's Twitter username."
                )),
                ('description', models.TextField(
                    blank=True, help_text='A description for the group.'
                )),
                ('logo', models.ImageField(
                    blank=True, help_text="Upload the group's logo."
                    " Its size must not exceed 2 MBs.",
                    storage=storage.OverwriteStorage(),
                    upload_to=uploaders.group_logo_uploader,
                    validators=[validators.FileSizeValidator(max_mb=2)]
                )),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('name', models.CharField(
                    help_text="The member's name.", max_length=100
                )),
                ('twitter', TwitterField(
                    blank=True, max_length=15,
                    help_text="The member's Twitter username."
                )),
                ('discord', DiscordNameField(
                    blank=True, max_length=37,
                    help_text="The member's Discord username and discriminator."
                )),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('role', models.CharField(
                    choices=[
                        ('LD', 'Leader'),
                        ('TL', 'Translator'),
                        ('PR', 'Proofreader'),
                        ('CL', 'Cleaner'),
                        ('RD', 'Redrawer'),
                        ('TS', 'Typesetter'),
                        ('RP', 'Raw Provider'),
                        ('QC', 'Quality Checker')
                    ], max_length=2
                )),
                ('group', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='roles', to='groups.Group'
                )),
                ('member', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='roles', to='groups.Member'
                )),
            ],
            options={
                'verbose_name': 'Role',
            },
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('member', 'role', 'group')},
        ),
    ]

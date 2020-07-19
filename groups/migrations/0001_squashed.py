from django.db import migrations, models

from MangAdventure import fields, storage, validators

from groups.models import _logo_uploader


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    # TODO: remove squashed migrations after application
    replaces = [
        ('groups', '0001_initial'),
        ('groups', '0002_irc_reddit'),
        ('groups', '0003_cdn_storage'),
    ]

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
                ('website', models.URLField(
                    blank=True, help_text="The group's website."
                )),
                ('email', models.EmailField(
                    blank=True, max_length=254,
                    help_text="The group's E-mail address."
                )),
                ('discord', fields.DiscordURLField(
                    blank=True, help_text="The group's Discord link."
                )),
                ('twitter', fields.TwitterField(
                    blank=True, max_length=15,
                    help_text="The group's Twitter username."
                )),
                ('description', models.TextField(
                    blank=True, help_text='A description for the group.'
                )),
                ('logo', models.ImageField(
                    blank=True, help_text=(
                        "Upload the group's logo. "
                        "Its size must not exceed 2 MBs."
                    ), upload_to=_logo_uploader,
                    storage=storage.CDNStorage((150, 150)),
                    validators=(validators.FileSizeValidator(2),)
                )),
                ('irc', models.CharField(
                    blank=True, max_length=63,
                    help_text="The group's IRC."
                )),
                (('reddit', fields.RedditField(
                    blank=True, help_text=(
                        "The group's Reddit username or "
                        "subreddit. (Include /u/ or /r/)"
                    ), max_length=24
                )))
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
                ('twitter', fields.TwitterField(
                    blank=True, max_length=15,
                    help_text="The member's Twitter username."
                )),
                ('discord', fields.DiscordNameField(
                    blank=True, max_length=37,
                    help_text="The member's Discord username and discriminator."
                )),
                ('irc', models.CharField(
                    blank=True, max_length=63,
                    help_text="The member's IRC username."
                )),
                (('reddit', fields.RedditField(
                    blank=True, max_length=21,
                    help_text="The member's Reddit username."
                )))
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
                    choices=(
                        ('LD', 'Leader'),
                        ('TL', 'Translator'),
                        ('PR', 'Proofreader'),
                        ('CL', 'Cleaner'),
                        ('RD', 'Redrawer'),
                        ('TS', 'Typesetter'),
                        ('RP', 'Raw Provider'),
                        ('QC', 'Quality Checker')
                    ), max_length=2
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
        migrations.AddField(
            model_name='member',
            name='groups',
            field=models.ManyToManyField(
                blank=False, related_name='members',
                through='groups.Role', to='groups.Group'
            )
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('member', 'role', 'group')},
        ),
    ]

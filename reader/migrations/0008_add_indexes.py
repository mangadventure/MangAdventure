from django.db import migrations, models

from MangAdventure.models import AliasField


class Migration(migrations.Migration):
    dependencies = [
        ('reader', '0007_editable_slugs'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page', options={
                'ordering': ('chapter', 'number')
            },
        ),
        migrations.AlterField(
            model_name='artist', name='name',
            field=models.CharField(
                max_length=100, db_index=True,
                help_text="The artist's full name."
            ),
        ),
        migrations.AlterField(
            model_name='artistalias', name='alias',
            field=AliasField(
                blank=True, db_index=True,
                help_text='Another name for the artist.',
                max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name='author', name='name',
            field=models.CharField(
                max_length=100, db_index=True,
                help_text="The author's full name."
            ),
        ),
        migrations.AlterField(
            model_name='authoralias', name='alias',
            field=AliasField(
                blank=True, db_index=True,
                help_text='Another name for the author.',
                max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name='chapter', name='uploaded',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='series', name='title',
            field=models.CharField(
                max_length=250, db_index=True,
                help_text='The title of the series.'
            ),
        ),
        migrations.AlterField(
            model_name='seriesalias', name='alias',
            field=AliasField(
                blank=True, db_index=True,
                help_text='Another title for the series.',
                max_length=250, unique=True
            ),
        ),
    ]

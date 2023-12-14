from django.db import migrations, models

from MangAdventure.storage import CDNStorage


def set_page_size(apps, schema_editor):
    page = apps.get_model('reader', 'Page')
    for p in page.objects.iterator():
        p.height = p.image.height
        p.width = p.image.width
        p.save(update_fields=('height', 'width'))


class Migration(migrations.Migration):
    dependencies = [('reader', '0011_series_status')]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.CharField(
                auto_created=True, max_length=25,
                primary_key=True, serialize=False
            )
        ),
        migrations.AddField(
            model_name='series',
            name='kind',
            field=models.CharField(
                choices=[
                    ('manga', 'Manga'),
                    ('comic', 'Comic'),
                    ('webtoon', 'Webtoon')
                ],
                default='manga', max_length=8,
                help_text='Determines the page layout.'
            )
        ),
        migrations.AddField(
            model_name='series',
            name='rating',
            field=models.CharField(
                choices=[
                    ('safe', 'Safe'),
                    ('suggestive', 'Suggestive'),
                    ('explicit', 'Explicit')
                ],
                default='safe', max_length=11,
                help_text='The content rating.'
            )
        ),
        migrations.AlterField(
            model_name='chapter',
            name='views',
            field=models.PositiveIntegerField(
                db_default=models.Value(0), db_index=True,
                editable=False, help_text='The total views of the chapter.'
            )
        ),
        migrations.AddField(
            model_name='chapter',
            name='cover',
            field=models.OneToOneField(
                null=True, on_delete=models.CASCADE,
                related_name='_cover_for', to='reader.page',
                help_text='The cover page of the chapter.'
            )
        ),
        migrations.AddField(
            model_name='page',
            name='position',
            field=models.CharField(
                default='center', max_length=1,
                help_text='Use "center" for webtoons and spreads.',
                choices=[('l', 'left'), ('r', 'right'), ('c', 'center')]
            ),
            preserve_default=False
        ),
        migrations.AddField(
            model_name='page',
            name='spread',
            field=models.BooleanField(
                default=False, help_text='Is this a double-page spread?'
            )
        ),
        migrations.AddField(
            model_name='page',
            name='height',
            field=models.PositiveIntegerField(default=0, editable=True),
            preserve_default=False
        ),
        migrations.AddField(
            model_name='page',
            name='width',
            field=models.PositiveIntegerField(default=0, editable=True),
            preserve_default=False
        ),
        migrations.RunPython(set_page_size, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='page',
            name='height',
            field=models.PositiveIntegerField(editable=False)
        ),
        migrations.AlterField(
            model_name='page',
            name='width',
            field=models.PositiveIntegerField(editable=False)
        ),
        migrations.AlterField(
            model_name='page',
            name='image',
            field=models.ImageField(
                height_field='height', width_field='width',
                max_length=255, upload_to='', storage=CDNStorage()
            )
        ),
    ]

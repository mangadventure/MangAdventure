from django.db import migrations, models


def populate_dates(apps, schema_editor):
    series = apps.get_model('reader', 'Series')
    series._meta.get_field('modified').auto_now = False
    for s in series.objects.prefetch_related('chapters').all():
        ch = s.chapters.only('uploaded').earliest('uploaded')
        s.created = ch.uploaded
        s.save()
    series._meta.get_field('modified').auto_now = True


class Migration(migrations.Migration):
    dependencies = [('reader', '0001_squashed')]

    operations = [
        migrations.AddField(
            model_name='series',
            name='created',
            field=models.DateTimeField(
                auto_now_add=False, db_index=True, null=True
            )
        ),
        migrations.RunPython(populate_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='series',
            name='created',
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, null=False
            )
        ),
        migrations.AddField(
            model_name='series',
            name='format',
            field=models.CharField(
                max_length=100, default='Vol. {volume}, Ch. {number}: {title}',
                help_text='The format used to render the chapter names.',
                verbose_name='chapter name format'
            )
        ),
    ]

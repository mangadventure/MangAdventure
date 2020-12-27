from django.db import migrations, models


def populate_aliases(apps, schema_editor):
    series = apps.get_model('reader', 'Series')
    author = apps.get_model('reader', 'Author')
    artist = apps.get_model('reader', 'Artist')
    alias = apps.get_model('reader', 'Alias')
    ct = apps.get_model('contenttypes', 'ContentType')
    sct = ct.objects.get_for_model(series)
    auct = ct.objects.get_for_model(author)
    arct = ct.objects.get_for_model(artist)
    for s in series.objects.iterator():
        alias.objects.bulk_create([
            alias(object_id=s.id, content_type=sct, name=a)
            for a in s.aliases.values_list('alias', flat=True)
        ])
    for au in author.objects.iterator():
        alias.objects.bulk_create([
            alias(object_id=au.id, content_type=auct, name=a)
            for a in s.aliases.values_list('alias', flat=True)
        ])
    for ar in artist.objects.iterator():
        alias.objects.bulk_create([
            alias(object_id=ar.id, content_type=arct, name=a)
            for a in s.aliases.values_list('alias', flat=True)
        ])


def populate_aliases_reverse(apps, schema_editor):
    from sys import argv  # isort:skip
    from django.core.management import color  # isort:skip
    answer = None
    if not set(argv) & {'--noinput', '--no-input'}:
        answer = input(color.color_style().WARNING(
            "\n  Aliases will be lost. Type 'yes'"
            " to continue, or 'no' to cancel: "
        ))
    if answer != 'yes':
        raise migrations.exceptions.IrreversibleError(
            f'Operation {populate_aliases} in '
            'reader.0004_aliases is not reversible'
        )
    print(end=' ')


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('reader', '0003_chapter_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('name', models.CharField(
                    db_index=True, max_length=255,
                    verbose_name='alias', blank=True
                )),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    to='contenttypes.ContentType'
                )),
            ],
            options={
                'verbose_name_plural': 'aliases',
                'unique_together': {('name', 'content_type', 'object_id')},
            },
        ),
        migrations.RunPython(populate_aliases, populate_aliases_reverse),
        migrations.RemoveField(model_name='artistalias', name='artist'),
        migrations.RemoveField(model_name='authoralias', name='author'),
        migrations.RemoveField(model_name='seriesalias', name='series'),
        migrations.DeleteModel(name='ArtistAlias'),
        migrations.DeleteModel(name='AuthorAlias'),
        migrations.DeleteModel(name='SeriesAlias'),
        migrations.AlterModelOptions(name='category', options={
            'ordering': ('id',), 'verbose_name_plural': 'categories'
        }),
    ]

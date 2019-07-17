from django.db import migrations, models

from MangAdventure.models import AliasKeyField


class Migration(migrations.Migration):
    def __init__(self, name, app_label):
        self.name = name
        self.app_label = app_label
        self.dependencies = [
            ('reader', '0006_remove_chapter_url'),
        ]
        self.operations = [
            migrations.AlterField(
                model_name='chapter', name='series',
                field=models.CharField(max_length=250, blank=True)
            ),
            migrations.AlterField(
                model_name='seriesalias', name='series',
                field=models.CharField(max_length=250, blank=True)
            ),
            migrations.RunPython(self.backup_m2m_fields),
            migrations.RemoveField(model_name='series', name='authors'),
            migrations.RemoveField(model_name='series', name='artists'),
            migrations.RemoveField(model_name='series', name='categories'),
            migrations.AlterField(
                model_name='series', name='slug',
                field=models.SlugField(
                    primary_key=False, blank=True,
                    unique=True, verbose_name='Custom slug',
                    help_text='The unique slug of the series.'
                              ' Will be used in the URL.'
                )
            ),
            migrations.AddField(
                model_name='series', name='id',
                field=models.AutoField(primary_key=True, serialize=False)
            ),
            migrations.RunPython(self.populate_ids),
            migrations.AddField(
                model_name='series', name='artists',
                field=models.ManyToManyField(blank=True, to='reader.Artist'),
            ),
            migrations.AddField(
                model_name='series', name='authors',
                field=models.ManyToManyField(blank=True, to='reader.Author'),
            ),
            migrations.AddField(
                model_name='series', name='categories',
                field=models.ManyToManyField(blank=True, to='reader.Category'),
            ),
            migrations.RunPython(self.populate_m2m_fields),
            migrations.AlterField(
                model_name='chapter', name='series',
                field=models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='chapters', to='reader.Series',
                    help_text='The series this chapter belongs to.'
                )
            ),
            migrations.AlterField(
                model_name='seriesalias', name='series',
                field=AliasKeyField(
                    on_delete=models.deletion.CASCADE, to='reader.Series'
                ),
            ),
        ]
        self.m2m_fields = []

    def backup_m2m_fields(self, apps, schema_editor):
        series = apps.get_model('reader', 'Series')
        for s in series.objects.all():
            self.m2m_fields.append({
                'slug': s.slug,
                'authors': list(s.authors.values_list('id', flat=True)),
                'artists': list(s.artists.values_list('id', flat=True)),
                'categories': list(s.categories.values_list('id', flat=True))
            })

    def populate_ids(self, apps, schema_editor):
        series = apps.get_model('reader', 'Series')
        chapter = apps.get_model('reader', 'Chapter')
        alias = apps.get_model('reader', 'SeriesAlias')
        for s in series.objects.all():
            s.save()
            for c in chapter.objects.filter(series=s.slug):
                c.series = s.id
                c.save()
            for a in alias.objects.filter(series=s.slug):
                a.series = s.id
                a.save()

    def populate_m2m_fields(self, apps, schema_editor):
        series = apps.get_model('reader', 'Series')
        authors = series.authors.through
        artists = series.artists.through
        categories = series.categories.through
        for fields in self.m2m_fields:
            s = series.objects.only('id').get(slug=fields['slug']).id
            authors.objects.bulk_create([
                authors(series_id=s, author_id=a)
                for a in fields['authors']
            ])
            artists.objects.bulk_create([
                artists(series_id=s, artist_id=a)
                for a in fields['artists']
            ])
            categories.objects.bulk_create([
                categories(series_id=s, category_id=c)
                for c in fields['categories']
            ])

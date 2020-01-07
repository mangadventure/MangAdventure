from django.db import migrations


def create_info_pages(apps, schema_editor):
    flatpage = apps.get_model('flatpages', 'FlatPage')
    site = apps.get_model('sites', 'Site')
    pages = flatpage.objects.bulk_create([
        flatpage(pk=1, url='/info/', title='About us'),
        flatpage(pk=2, url='/privacy/', title='Privacy')
    ])
    for page in pages:
        page.sites.set(site.objects.filter(pk=1))


def remove_info_pages(apps, schema_editor):
    flatpage = apps.get_model('flatpages', 'FlatPage')
    flatpage.objects.all().delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('flatpages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_info_pages, remove_info_pages),
    ]

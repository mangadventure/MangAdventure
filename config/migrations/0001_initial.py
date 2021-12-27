from django.db import migrations


def create_info_pages(apps, schema_editor):
    from django.conf import settings
    apps.get_model('sites', 'Site').objects.create(
        pk=settings.SITE_ID,
        name=settings.CONFIG['NAME'],
        domain=settings.CONFIG['DOMAIN']
    )
    flatpage = apps.get_model('flatpages', 'FlatPage')
    flatpage.objects.bulk_create([
        flatpage(pk=1, url='/info/', title='About us'),
        flatpage(pk=2, url='/privacy/', title='Privacy')
    ])
    through = flatpage.sites.through
    through.objects.bulk_create([
        through(flatpage_id=1, site_id=settings.SITE_ID),
        through(flatpage_id=2, site_id=settings.SITE_ID)
    ])


def remove_info_pages(apps, schema_editor):
    from django.conf import settings
    apps.get_model('flatpages', 'FlatPage').objects.all().delete()
    apps.get_model('sites', 'Site').get(pk=settings.SITE_ID).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [('flatpages', '0001_initial')]

    operations = [migrations.RunPython(create_info_pages, remove_info_pages)]

from django.db import migrations


def add_scanlator_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    permission = apps.get_model('auth', 'Permission')
    scanlator = group.objects.create(name='Scanlator')
    scanlator.permissions.set(permission.objects.filter(
        content_type__app_label__in=('reader', 'groups')
    ))
    scanlator.save()


def remove_scanlator_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    group.objects.get(name='Scanlator').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('config', '0001_initial'),
        ('auth', '0001_initial'),
        ('reader', '0004_aliases'),
        ('groups', '0001_squashed'),
    ]

    operations = [
        migrations.RunPython(add_scanlator_group, remove_scanlator_group)
    ]

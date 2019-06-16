from os.path import dirname, join
from shutil import move

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Chapter, Series


def _move(old_dir, new_dir):
    try:
        move(
            join(settings.MEDIA_ROOT, old_dir),
            join(settings.MEDIA_ROOT, new_dir)
        )
    except OSError as e:
        if e.errno == 2: pass
        else: raise e


@receiver(pre_save, sender=Series)
def redirect_series(sender, instance, **kwargs):
    if instance.id:
        current = Series.objects.get(id=instance.id)
        if current.slug != instance.slug:
            old_path = current.get_absolute_url()
            new_path = instance.get_absolute_url()
            # Update any existing redirects that are pointing to the old path
            for redirect in Redirect.objects.filter(new_path=old_path):
                redirect.new_path = new_path
                if redirect.new_path == redirect.old_path:
                    redirect.delete()
                else:
                    redirect.save()
            # Now add the new redirect
            Redirect.objects.create(
                site_id=settings.SITE_ID, old_path=old_path, new_path=new_path
            )
            _move(current.get_directory(), instance.get_directory())
            instance.cover = join(
                instance.get_directory(), instance.cover.name
            )
            for chapter in instance.chapters.prefetch_related('pages').all():
                for page in chapter.pages.all():
                    page.image = page.image.name.replace(
                        current.get_directory(), instance.get_directory()
                    )
                    page.save()


@receiver(pre_save, sender=Chapter)
def redirect_chapter(sender, instance, **kwargs):
    if instance.id:
        current = Chapter.objects.get(id=instance.id)
        if current.get_directory() != instance.get_directory():
            if current.volume != instance.volume:
                _move(
                    dirname(current.get_directory()),
                    dirname(instance.get_directory())
                )
            if current.number != instance.number:
                _move(current.get_directory(), instance.get_directory())
            for page in current.pages.all():
                page.image = page.image.name.replace(
                    current.get_directory(), instance.get_directory()
                )
                page.save()

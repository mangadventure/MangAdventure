from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Chapter, Series


def _move(old_dir, new_dir):
    new_path = settings.MEDIA_ROOT / new_dir
    if not new_path.exists():
        old_path = settings.MEDIA_ROOT / old_dir
        old_path.rename(new_path)


@receiver(pre_save, sender=Series)
def redirect_series(sender, instance, **kwargs):
    if instance.id:
        try:
            current = Series.objects.get(id=instance.id)
        except Series.DoesNotExist:
            return
        if current.slug != instance.slug:
            old_path = current.get_absolute_url()
            old_dir = current.get_directory()
            new_path = instance.get_absolute_url()
            new_dir = instance.get_directory()
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
            _move(old_dir, new_dir)
            instance.cover = instance.cover.name.replace(
                str(old_dir), str(new_dir)
            )
            for chapter in instance.chapters.prefetch_related('pages').all():
                for page in chapter.pages.all():
                    page.image = page.image.name.replace(
                        str(old_dir), str(new_dir)
                    )
                    page.save()


@receiver(pre_save, sender=Chapter)
def redirect_chapter(sender, instance, **kwargs):
    if instance.id:
        try:
            current = Chapter.objects.get(id=instance.id)
        except Chapter.DoesNotExist:
            return
        old_dir = current.get_directory()
        new_dir = instance.get_directory()
        if old_dir != new_dir:
            if current.volume != instance.volume:
                _move(old_dir.name, new_dir.name)
            if current.number != instance.number:
                _move(old_dir, new_dir)
            for page in current.pages.all():
                page.image = page.image.name.replace(
                    str(old_dir), str(new_dir)
                )
                page.save()

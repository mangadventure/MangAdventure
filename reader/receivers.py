"""Signal receivers for the reader app."""

from typing import Type

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Chapter, Series


def _move(old_dir: str, new_dir: str):
    new_path = settings.MEDIA_ROOT / new_dir
    if not new_path.exists():
        old_path = settings.MEDIA_ROOT / old_dir
        old_path.rename(new_path)


@receiver(pre_save, sender=Series)
def redirect_series(sender: Type[Series], instance: Series, **kwargs):
    """
    Receive a signal when a series is about to be saved.

    If the series exists and its slug has changed,
    rename its directory and create a new
    :class:`~django.contrib.redirects.models.Redirect`.

    :param sender: The model class that sent the signal.
    :param instance: The instance of the model.
    """
    if not instance.id:
        return
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
        _move(old_dir, str(new_dir))
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
def redirect_chapter(sender: Type[Chapter], instance: Chapter, **kwargs):
    """
    Receive a signal when a series is about to be saved.

    If the chapter exists and the slug of the series
    it belongs to has changed, rename its directory.

    :param sender: The model class that sent the signal.
    :param instance: The instance of the model.
    """
    if not instance.id:
        return
    try:
        current = Chapter.objects.get(id=instance.id)
    except Chapter.DoesNotExist:
        return
    old_dir = current.get_directory()
    new_dir = instance.get_directory()
    if old_dir != new_dir:
        if current.volume != instance.volume:
            _move(str(old_dir.parent), str(new_dir.parent))
            old_dir = new_dir.parent / old_dir.name
        if current.number != instance.number:
            _move(old_dir, str(new_dir))
        for page in current.pages.all():
            page.image = page.image.name.replace(
                str(old_dir), str(new_dir)
            )
            page.save()


__all__ = ['redirect_series', 'redirect_chapter']

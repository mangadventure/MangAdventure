"""Signal receivers for the reader app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIHandler
from django.core.signals import request_started
from django.db.models import signals
from django.dispatch import receiver
from django.http.request import QueryDict
from django.urls.base import resolve
from django.urls.exceptions import Resolver404
from django.utils.text import slugify

from .models import Chapter, Page, Series

if TYPE_CHECKING:  # pragma: no cover
    from os import PathLike


def _move(old_dir: PathLike, new_dir: PathLike):
    if not (new_path := settings.MEDIA_ROOT / new_dir).exists():
        old_path = settings.MEDIA_ROOT / old_dir
        old_path.rename(new_path)


@receiver(signals.pre_save, sender=Series)
def redirect_series(sender: type[Series], instance: Series, **kwargs):
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
    # update the slug while we're at it
    if current.title != instance.title and \
            current.slug == instance.slug == slugify(current.title):
        instance.slug = slugify(instance.title)
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
        # Now add the new redirects
        Redirect.objects.bulk_create([
            Redirect(site_id=site_id, old_path=old_path, new_path=new_path)
            for site_id in Site.objects.values_list('id', flat=True)
        ])
        _move(old_dir, new_dir)
        instance.cover = instance.cover.name.replace(
            str(old_dir), str(new_dir)
        )
        for chapter in instance.chapters.prefetch_related('pages').all():
            pages = chapter.pages.all()
            for page in pages:
                page.image = page.image.name.replace(
                    str(old_dir), str(new_dir)
                )
            Page.objects.bulk_update(pages, ('image',))


@receiver(signals.pre_save, sender=Chapter)
def redirect_chapter(sender: type[Chapter], instance: Chapter, **kwargs):
    """
    Receive a signal when a chapter is about to be saved.

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
            _move(old_dir.parent, new_dir.parent)
            old_dir = new_dir.parent / old_dir.name
        if current.number != instance.number:
            _move(old_dir, new_dir)
            for page in (pages := current.pages.all()):
                page.image = page.image.name.replace(
                    str(old_dir), str(new_dir)
                )
            Page.objects.bulk_update(pages, ('image',))


@receiver(signals.pre_save, sender=Chapter)
def complete_series(sender: type[Chapter], instance: Chapter, **kwargs):
    """
    Receive a signal when a chapter is about to be saved.

    If the chapter is new and has been marked as final,
    set the status of the series it belongs to as "Completed".

    :param sender: The model class that sent the signal.
    :param instance: The instance of the model.
    """
    if not instance.id and instance.final:  # type: ignore
        instance.series.status = 'completed'  # type: ignore
        instance.series.save(update_fields=('status',))  # type: ignore


@receiver(signals.post_save, sender=Chapter)
def clear_chapter_cache(sender: type[Chapter], instance:
                        Chapter, created: bool, **kwargs):
    """
    Receive a signal when a chapter has been saved.

    Delete the relevant cache keys

    :param sender: The model class that sent the signal.
    :param instance: The instance of the model.
    :param created: Whether a new instance was created.
    """
    if created:
        cache.delete(f'reader.chapters.{instance.series.slug}')


# TODO: figure out how to test this
@receiver(request_started, sender=WSGIHandler)
def track_view(sender: type[WSGIHandler], environ:
               dict[str, str], **kwargs):  # pragma: no cover
    """
    Receive a signal when a request is processed.

    Track the chapter view if necessary.

    :param sender: The request handler class that sent the signal.
    :param environ: The metadata dictionary provided to the request.
    """
    try:
        url = resolve(environ.get('PATH_INFO', ''))
    except Resolver404:
        return

    if url.url_name == 'page':
        try:
            args_ = url.captured_kwargs  # type: ignore
            if args_['page'] == 1:
                Chapter.track_view(
                    series__licensed=False,
                    series__slug=args_['slug'],
                    volume=args_['volume'] or None,
                    number=args_['number']
                )
        except KeyError:
            return
    elif url.url_name == 'chapters-pages':
        q = QueryDict(environ.get('QUERY_STRING', ''))
        if q.get('track', '') == 'true':
            try:
                Chapter.track_view(
                    series__licensed=False,
                    id=int(url.captured_kwargs['pk'])  # type: ignore
                )
            except (KeyError, ValueError):
                return


__all__ = [
    'redirect_series', 'redirect_chapter',
    'complete_series', 'clear_chapter_cache', 'track_view'
]

"""The views of the reader app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, F, Prefetch, Q
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone as tz
from django.views.decorators.cache import cache_control
from django.views.decorators.http import condition

from MangAdventure import jsonld
from MangAdventure.utils import HttpResponseUnauthorized

from groups.models import Group

from .models import Chapter, Series

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime  # isort:skip
    from typing import Optional, Union  # isort:skip
    from django.http import (  # isort:skip
        HttpRequest, HttpResponse, HttpResponsePermanentRedirect
    )


def _latest(request: HttpRequest, slug: Optional[str] = None,
            vol: Optional[int] = None, num: Optional[float] = None,
            page: Optional[int] = None) -> Optional[datetime]:
    try:
        if slug is None:
            q = Q(chapters__published__lte=tz.now())
            return Series.objects.only('modified').alias(
                chapter_count=Count('chapters', filter=q)
            ).filter(chapter_count__gt=0).latest().modified
        if vol is None:
            return Series.objects.only('modified').filter(
                chapters__published__lte=tz.now(), slug=slug
            ).distinct().get().modified
        return Chapter.objects.only('modified').filter(
            series__slug=slug, volume=vol or None,
            number=num, published__lte=tz.now()
        ).latest().modified
    except (Series.DoesNotExist, Chapter.DoesNotExist):
        return None


def _cbz_etag(request: HttpRequest, slug: str, vol: int, num: float) -> str:
    return 'W/"%x"' % (hash(f'{slug}-{vol}-{num}.cbz') & (1 << 64) - 1)


@condition(last_modified_func=_latest)
@cache_control(max_age=600, must_revalidate=True)
def directory(request: HttpRequest) -> HttpResponse:
    """
    View that serves a page which lists all the series.

    :param request: The original request.

    :return: A response with the rendered ``all_series.html`` template.
    """
    chapters = Chapter.objects.filter(
        published__lte=tz.now()
    ).order_by('-published').defer(
        'file', 'views', 'modified'
    )
    groups = Group.objects.only('name')
    q = Q(chapters__published__lte=tz.now())
    series = list(Series.objects.alias(
        chapter_count=Count('chapters', filter=q)
    ).filter(chapter_count__gt=0).prefetch_related(
        Prefetch('chapters', queryset=chapters),
        Prefetch('chapters__groups', queryset=groups)
    ).distinct().order_by('title').only(
        'title', 'slug', 'format', 'cover'
    ).exclude(licensed=True))
    uri = request.build_absolute_uri(request.path)
    crumbs = jsonld.breadcrumbs([('Reader', uri)])
    library = jsonld.carousel([s.get_absolute_url() for s in series])
    return render(request, 'directory.html', {
        'all_series': series,
        'library': library,
        'breadcrumbs': crumbs
    })


@condition(last_modified_func=_latest)
@cache_control(max_age=1800, must_revalidate=True)
def series(request: HttpRequest, slug: str) -> HttpResponse:
    """
    View that serves the page of a single series.

    If the series doesn't have any published chapters,
    only staff members will be able to see it.

    :param request: The original request.
    :param slug: The slug of the series.

    :return: A response with the rendered ``series.html`` template.

    :raises Http404: If there is no series with the specified ``slug``.
    """
    try:
        chapters = Chapter.objects.filter(
            published__lte=tz.now()
        ).order_by(
            'series', F('volume').asc(nulls_last=True), 'number'
        ).reverse().defer('file', 'views', 'modified')
        groups = Group.objects.only('name')
        series = Series.objects.prefetch_related(
            Prefetch('chapters', queryset=chapters),
            Prefetch('chapters__groups', queryset=groups),
            Prefetch('authors'), Prefetch('artists')
        ).defer('manager').get(slug=slug)
    except Series.DoesNotExist as e:
        raise Http404 from e
    chapters = None if series.licensed else list(series.chapters.all())
    if not series.licensed and not chapters:
        return render(request, 'error.html', {
            'error_message': 'Sorry. This series is not yet available.',
            'error_status': 403
        }, status=403)
    marked = request.user.is_authenticated and \
        request.user.bookmarks.filter(series=series).exists()
    url = request.path
    p_url = url.rsplit('/', 2)[0] + '/'
    uri = request.build_absolute_uri(url)
    crumbs = jsonld.breadcrumbs([
        ('Reader', request.build_absolute_uri(p_url)),
        (series.title, uri)
    ])
    tags = list(series.categories.values_list('name', flat=True))
    authors = list(series.authors.all())
    artists = list(series.artists.all())
    aliases = series.aliases.names()
    book = jsonld.schema('Book', {
        'url': uri,
        'name': series.title,
        'abstract': series.description,
        'author': [{
            '@type': 'Person',
            'name': au.name,
            # 'alternateName': au.aliases.names()
        } for au in authors],
        'illustrator': [{
            '@type': 'Person',
            'name': ar.name,
            # 'alternateName': ar.aliases.names()
        } for ar in artists],
        'alternateName': aliases,
        'creativeWorkStatus': (
            'Published' if series.completed else 'Incomplete'
        ),
        'isAccessibleForFree': not series.licensed,
        'dateCreated': series.created.strftime('%F'),
        'dateModified': series.modified.strftime('%F'),
        'bookFormat': 'GraphicNovel',
        'genre': tags,
    })
    return render(request, 'series.html', {
        'series': series,
        'chapters': chapters,
        'marked': marked,
        'breadcrumbs': crumbs,
        'book_ld': book,
        'authors': authors,
        'artists': artists,
        'aliases': aliases,
        'tags': tags
    })


@condition(last_modified_func=_latest)
@cache_control(max_age=3600, must_revalidate=True)
def chapter_page(request: HttpRequest, slug: str, vol: int,
                 num: float, page: int) -> HttpResponse:
    """
    View that serves a chapter page.

    :param request: The original request.
    :param slug: The slug of the series.
    :param vol: The volume of the chapter.
    :param num: The number of the chapter.
    :param page: The number of the page.

    :return: A response with the rendered ``chapter.html`` template.

    :raises Http404: If there is no matching chapter or page.
    """
    if page == 0:
        raise Http404('Page cannot be 0')
    chapters = list(Chapter.objects.filter(
        series__slug=slug,
        series__licensed=False,
        published__lte=tz.now()
    ).select_related('series').only(
        'title', 'number', 'volume', 'published',
        'final', 'series__slug', 'series__cover',
        'series__title', 'series__format'
    ).order_by(
        'series', F('volume').asc(nulls_last=True), 'number'
    ).reverse())
    if not chapters:
        raise Http404('No chapters for this series')
    max_, found = len(chapters) - 1, False
    for idx, current in enumerate(chapters):
        if current == (vol or float('inf'), num):
            next_ = chapters[idx - 1] if idx > 0 else None
            prev_ = chapters[idx + 1] if idx < max_ else None
            found = True
            break
    if not found:
        raise Http404('No such chapter')
    if page == 1:
        Chapter.track_view(id=current.id)
    all_pages = list(current.pages.all())
    try:
        curr_page = next(p for p in all_pages if p.number == page)
    except StopIteration as e:
        raise Http404('No such page') from e
    preload = list(filter(
        lambda p: curr_page < p < curr_page.number + 4, all_pages
    ))
    tags = current.series.categories.values_list('name', flat=True)
    url = request.path
    p_url = url.rsplit('/', 4)[0] + '/'
    p2_url = url.rsplit('/', 5)[0] + '/'
    crumbs = jsonld.breadcrumbs([
        ('Reader', request.build_absolute_uri(p2_url)),
        (current.series.title, request.build_absolute_uri(p_url)),
        (current.title, request.build_absolute_uri(url))
    ])
    return render(request, 'chapter.html', {
        'all_chapters': chapters,
        'curr_chapter': current,
        'next_chapter': next_,
        'prev_chapter': prev_,
        'all_pages': all_pages,
        'curr_page': curr_page,
        'preload': preload,
        'breadcrumbs': crumbs,
        'tags': ','.join(tags)
    })


def chapter_redirect(request: HttpRequest, slug: str, vol: int,
                     num: float) -> HttpResponsePermanentRedirect:
    """
    View that redirects a chapter to its first page.

    :param request: The original request.
    :param slug: The slug of the series.
    :param vol: The volume of the chapter.
    :param num: The number of the chapter.

    :return: A redirect to :func:`chapter_page`.
    """
    return redirect('reader:page', slug, vol, num, 1, permanent=True)


@condition(etag_func=_cbz_etag, last_modified_func=_latest)
@cache_control(public=True, max_age=3600)
def chapter_download(request: HttpRequest, slug: str, vol: int, num: float
                     ) -> Union[FileResponse, HttpResponseUnauthorized]:
    """
    View that generates a ``.cbz`` file from a chapter.

    :param request: The original request.
    :param slug: The slug of the chapter's series.
    :param vol: The volume of the chapter.
    :param num: The number of the chapter.

    :return: A response with the ``.cbz`` file if the user is logged in.

    :raises Http404: If the chapter does not exist.
    """
    if not request.user.is_authenticated:
        return HttpResponseUnauthorized(
            b'You must be logged in to download this file.',
            content_type='text/plain', realm='chapter archive'
        )
    try:
        chapter = Chapter.objects.only(
            'series__title', 'volume', 'number'
        ).select_related('series').get(
            series__slug=slug, series__licensed=False,
            volume=vol or None, number=num, published__lte=tz.now()
        )
    except Chapter.DoesNotExist as e:
        raise Http404 from e
    if chapter.volume:
        name = '{0.series} - v{0.volume} c{0.number:g}.cbz'.format(chapter)
    else:  # pragma: no cover
        name = '{0.series} - c{0.number:g}.cbz'.format(chapter)
    return FileResponse(
        chapter.zip(), as_attachment=True, filename=name,
        content_type='application/vnd.comicbook+zip'
    )


__all__ = [
    'directory', 'series', 'chapter_page',
    'chapter_redirect', 'chapter_download'
]

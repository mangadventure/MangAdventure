"""The views of the reader app."""

from typing import TYPE_CHECKING

from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import condition

from MangAdventure import jsonld

from .models import Chapter, Page, Series

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional
    from django.db.models import DateTimeField
    from django.http import (
        HttpRequest, HttpResponse,
        HttpResponsePermanentRedirect
    )


def _latest(request: 'HttpRequest', slug: 'Optional[str]' = None,
            vol: 'Optional[int]' = None, num: 'Optional[float]' = None,
            page: 'Optional[int]' = None) -> 'Optional[DateTimeField]':
    try:
        if slug is None:
            return Series.objects.only('modified').latest().modified
        if vol is None:
            return Series.objects.only('modified').get(slug=slug).modified
        return Chapter.objects.only('modified').filter(
            series__slug=slug, volume=vol, number=num
        ).latest().modified
    except (Series.DoesNotExist, Chapter.DoesNotExist):
        return None


def _cbz_etag(request: 'HttpRequest', slug: str, vol: int, num: float) -> str:
    return 'W/"%x"' % (hash(f'{slug}-{vol}-{num}.cbz') & (1 << 64) - 1)


@condition(last_modified_func=_latest)
@cache_control(max_age=600, must_revalidate=True)
def directory(request: 'HttpRequest') -> 'HttpResponse':
    """
    View that serves a page which lists all the series.

    :param request: The original request.

    :return: A response with the rendered ``all_series.html`` template.
    """
    _series = Series.objects.prefetch_related('chapters').order_by('title')
    uri = request.build_absolute_uri(request.path)
    crumbs = jsonld.breadcrumbs([('Reader', uri)])
    library = jsonld.carousel([s.get_absolute_url() for s in _series])
    return render(request, 'directory.html', {
        'all_series': _series,
        'library': library,
        'breadcrumbs': crumbs
    })


@condition(last_modified_func=_latest)
@cache_control(max_age=3600, must_revalidate=True)
def series(request: 'HttpRequest', slug: str) -> 'HttpResponse':
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
        _series = Series.objects.prefetch_related(
            'chapters__groups', 'artists', 'categories', 'authors', 'aliases'
        ).get(slug=slug)
    except Series.DoesNotExist as e:
        raise Http404 from e
    if not (request.user.is_staff or _series.chapters.count()):
        return render(request, 'error.html', {
            'error_message': 'Sorry. This series is not yet available.',
            'error_status': 403
        }, status=403)
    marked = (
        request.user.is_authenticated and
        request.user.bookmarks.filter(series=_series).exists()
    )
    url = request.path
    p_url = url.rsplit('/', 2)[0] + '/'
    uri = request.build_absolute_uri(url)
    crumbs = jsonld.breadcrumbs([
        ('Reader', request.build_absolute_uri(p_url)),
        (_series.title, uri)
    ])
    book = jsonld.schema('Book', {
        'url': uri,
        'name': _series.title,
        'abstract': _series.description,
        'author': [{
            '@type': 'Person',
            'name': au.name,
            'alternateName': [
                al.alias for al in au.aliases.all()
            ]
        } for au in _series.authors.all()],
        'illustrator': [{
            '@type': 'Person',
            'name': ar.name,
            'alternateName': [
                al.alias for al in ar.aliases.all()
            ]
        } for ar in _series.artists.all()],
        'alternateName': [
            al.alias for al in _series.aliases.all()
        ],
        'genre': [
            c.name for c in _series.categories.all()
        ],
        'creativeWorkStatus': (
            'Published' if _series.completed else 'Incomplete'
        ),
        'dateModified': _series.modified,
        'bookFormat': 'GraphicNovel',
    })
    return render(request, 'series.html', {
        'series': _series,
        'marked': marked,
        'breadcrumbs': crumbs,
        'book_ld': book
    })


@condition(last_modified_func=_latest)
@cache_control(max_age=3600, must_revalidate=True)
def chapter_page(request: 'HttpRequest', slug: str, vol: int,
                 num: float, page: int) -> 'HttpResponse':
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
    chapters = Chapter.objects.filter(series__slug=slug)
    try:
        current = chapters.select_related('series') \
            .prefetch_related('pages').get(volume=vol, number=num)
        all_pages = current.pages.all()
        curr_page = all_pages.get(number=page)
    except (Chapter.DoesNotExist, Page.DoesNotExist) as e:
        raise Http404 from e
    url = request.path
    p_url = url.rsplit('/', 4)[0] + '/'
    p2_url = url.rsplit('/', 5)[0] + '/'
    crumbs = jsonld.breadcrumbs([
        ('Reader', request.build_absolute_uri(p2_url)),
        (current.series.title, request.build_absolute_uri(p_url)),
        (current.title, request.build_absolute_uri(url))
    ])
    return render(request, 'chapter.html', {
        'all_chapters': chapters.reverse(),
        'curr_chapter': current,
        'next_chapter': current.next,
        'prev_chapter': current.prev,
        'all_pages': all_pages,
        'curr_page': curr_page,
        'breadcrumbs': crumbs
    })


def chapter_redirect(request: 'HttpRequest', slug: str, vol: int,
                     num: float) -> 'HttpResponsePermanentRedirect':
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
def chapter_download(request: 'HttpRequest', slug: str,
                     vol: int, num: float) -> FileResponse:
    """
    View that generates a ``.cbz`` file from a chapter.

    :param request: The original request.
    :param slug: The slug of the chapter's series.
    :param vol: The volume of the chapter.
    :param num: The number of the chapter.

    :return: A response with the ``.cbz`` file.
    """
    try:
        _chapter = Chapter.objects.get(
            series__slug=slug, volume=vol, number=num
        )
    except Chapter.DoesNotExist as e:
        raise Http404 from e
    mime = 'application/vnd.comicbook+zip'
    name = '{0.series} - v{0.volume} c{0.number:g}.cbz'.format(_chapter)
    return FileResponse(
        _chapter.zip(), as_attachment=True,
        filename=name, content_type=mime
    )


# def chapter_comments(request, slug, vol, num):
#     try:
#         chapter = Chapter.objects.get(
#             series__slug=slug, volume=vol, number=num
#         )
#     except Chapter.DoesNotExist as e:
#         raise Http404 from e
#     return render(request, 'comments.html', {'chapter': chapter})


__all__ = [
    'directory', 'series', 'chapter_page',
    'chapter_redirect', 'chapter_download'
]

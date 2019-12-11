"""The views of the reader app."""

from typing import TYPE_CHECKING

from django.http import Http404, FileResponse
from django.shortcuts import redirect, render

from .models import Chapter, Page, Series

if TYPE_CHECKING:
    from django.http import (
        HttpRequest, HttpResponse,
        HttpResponsePermanentRedirect
    )


def directory(request: 'HttpRequest') -> 'HttpResponse':
    """
    View that serves a page which lists all the series.

    :param request: The original request.

    :return: A response with the rendered ``all_series.html`` template.
    """
    _series = Series.objects.prefetch_related('chapters').order_by('title')
    return render(request, 'directory.html', {'all_series': _series})


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
    except Series.DoesNotExist:
        raise Http404
    if not (request.user.is_staff or _series.chapters.count()):
        return render(request, 'error.html', {
            'error_message': 'Sorry. This series is not yet available.',
            'error_status': 403
        }, status=403)
    marked = (
        request.user.is_authenticated and
        request.user.bookmarks.filter(series=_series).exists()
    )
    return render(request, 'series.html', {'series': _series, 'marked': marked})


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
        raise Http404
    chapters = Chapter.objects.filter(series__slug=slug)
    try:
        current = chapters.select_related('series') \
            .prefetch_related('pages').get(volume=vol, number=num)
        all_pages = current.pages.all()
        curr_page = all_pages.get(number=page)
    except (Chapter.DoesNotExist, Page.DoesNotExist):
        raise Http404
    return render(request, 'chapter.html', {
        'all_chapters': chapters.reverse(),
        'curr_chapter': current,
        'next_chapter': current.next,
        'prev_chapter': current.prev,
        'all_pages': all_pages,
        'curr_page': curr_page
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


def chapter_download(request: 'HttpRequest', slug: str,
                     vol: int, num: float) -> FileResponse:
    """
    View that generates a ``.cbz`` file from a chapter.

    .. admonition:: TODO
       :class: warning

       Add a download link on the series page.

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
    except Chapter.DoesNotExist:
        raise Http404
    mime = 'application/vnd.comicbook+zip'
    name = '{0.series} - v{0.volume} c{0.number:g}.cbz'.format(_chapter)
    return FileResponse(
        _chapter.zip(), as_attachment=True,
        filename=name, content_type=mime
    )


# def chapter_comments(request, slug, vol, num):
#     try:
#         chapter = Chapter.objects.get(
#             series__slug=slug, volume=int(vol), number=float(num)
#         )
#     except (ValueError, TypeError, Chapter.DoesNotExist):
#         raise Http404
#     return render(request, 'comments.html', {'chapter': chapter})


__all__ = [
    'directory', 'series', 'chapter_page',
    'chapter_redirect', 'chapter_download'
]

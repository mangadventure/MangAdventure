from django.http import Http404
from django.shortcuts import redirect, render

from .models import Chapter, Series, Page


def directory(request):
    _series = Series.objects.prefetch_related('chapters').order_by('title')
    return render(request, 'directory.html', {'all_series': _series})


def series(request, slug):
    try:
        _series = Series.objects.prefetch_related(
            'chapters__groups', 'artists', 'categories', 'authors', 'aliases'
        ).get(slug=slug)
    except Series.DoesNotExist:
        raise Http404
    if not (_series.chapters.count() or request.user.is_staff):
        return render(request, 'error.html', {
            'error_message': 'Sorry. This series is not yet available.',
            'error_status': 403
        }, status=403)
    marked = (
        request.user.is_authenticated and
        request.user.bookmarks.filter(series=_series).exists()
    )
    return render(request, 'series.html', {'series': _series, 'marked': marked})


def chapter_page(request, slug, vol, num, page):
    try:
        vol, num, page = int(vol), float(num), int(page)
    except (ValueError, TypeError):
        raise Http404
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


def chapter_redirect(request, slug, vol, num):
    return redirect('reader:page', slug, vol, num, 1, permanent=True)


# def chapter_comments(request, slug, vol, num):
#     try:
#         chapter = Chapter.objects.get(
#             series__slug=slug, volume=int(vol), number=float(num)
#         )
#     except (ValueError, TypeError, Chapter.DoesNotExist):
#         raise Http404
#     return render(request, 'comments.html', {'chapter': chapter})

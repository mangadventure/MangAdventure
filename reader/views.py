from django.http import Http404
from django.shortcuts import redirect, render

from next_prev import next_in_order, prev_in_order

from .models import Chapter, Series


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
    marked = request.user.is_authenticated and \
        request.user.bookmarks.filter(series=_series).exists()
    return render(request, 'series.html', {'series': _series, 'marked': marked})


def chapter_page(request, slug, vol, num, page):
    try:
        vol, num, page = int(vol), float(num), int(page)
    except (ValueError, TypeError):
        raise Http404
    if page == 0:
        return render(request, 'series.html', {'series': _series, 'marked': marked})

    chapters = {
        'all': Chapter.objects.filter(series__slug=slug),
        'curr': None,
        'prev': None,
        'next': None
    }
    try:
        chapters['curr'] = chapters['all'] \
            .prefetch_related('pages').get(number=num, volume=vol)
    except Chapter.DoesNotExist:
        raise Http404
    chapters['next'] = next_in_order(chapters['curr'], qs=chapters['all'])
    chapters['prev'] = prev_in_order(chapters['curr'], qs=chapters['all'])
    all_pages = chapters['curr'].pages.all()
    if page > len(all_pages):
        return render(request, 'series.html', {'series': _series, 'marked': marked})


    return render(request, 'chapter.html', {
        'all_chapters': chapters['all'].reverse(),
        'curr_chapter': chapters['curr'],
        'next_chapter': chapters['next'],
        'prev_chapter': chapters['prev'],
        'all_pages': all_pages,
        'curr_page': all_pages.get(number=page)
    })


def chapter_redirect(request, slug, vol, num):
    return redirect('reader:page', slug, vol, num, 1, permanent=True)

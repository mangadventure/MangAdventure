from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import Http404
from next_prev import next_in_order, prev_in_order
from .models import Chapter, Series


def directory(request):
    return render(request, 'directory.html', {
        'all_series': Series.objects.prefetch_related(
            'chapters').order_by('title')
    })


def series(request, slug=None):
    try:
        _series = Series.objects.prefetch_related(
            'chapters__groups', 'artists', 'categories',
            'authors', 'aliases').get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404
    if not (_series.chapters.count() or request.user.is_staff):
        return render(request, 'error.html', {
            'error_message': 'Sorry. This series is not yet available.',
            'error_status': 403
        }, status=403)
    return render(request, 'series.html', {'series': _series})


def chapter_page(request, slug=None, vol=0, num=0, page=1):
    try:
        vol, num, page = int(vol), float(num), int(page)
    except (ValueError, TypeError):
        raise Http404
    if page == 0:
        raise Http404
    chapters = {
        'all': Chapter.objects.prefetch_related(
            'series__categories', 'pages').filter(series_id=slug),
        'curr': None,
        'prev': None,
        'next': None
    }
    try:
        chapters['curr'] = chapters['all'].get(number=num, volume=vol)
    except ObjectDoesNotExist:
        raise Http404
    chapters['next'] = next_in_order(chapters['curr'])
    chapters['prev'] = prev_in_order(chapters['curr'])
    all_pages = chapters['curr'].pages.all()
    if page > len(all_pages):
        raise Http404
    return render(request, 'chapter.html', {
        'all_chapters': chapters['all'].reverse(),
        'curr_chapter': chapters['curr'],
        'next_chapter': chapters['next'],
        'prev_chapter': chapters['prev'],
        'all_pages': all_pages,
        'curr_page': all_pages.get(number=page)
    })


def chapter_redirect(request, slug=None, vol=0, num=0):
    return redirect('reader:page', permanent=True,
                    slug=slug, vol=vol, num=num, page=1)


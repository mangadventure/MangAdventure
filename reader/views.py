from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import Http404
from next_prev import next_in_order, prev_in_order
from constance import config
from .models import Chapter, Series


def _get_url(request): return request.get_raw_uri().split('?')[0]


def index(request):
    maximum = config.MAX_RELEASES
    releases = Chapter.objects.all().order_by('-date')[:maximum:1]
    return render(request, 'index.html', {
        'latest_releases': releases,
        'page_url': _get_url(request)
    })


def directory(request):
    return render(request, 'directory.html', {
        'all_series': Series.objects.all().order_by('title'),
        'page_url': _get_url(request)
    })


def series(request, slug=None):
    try:
        _series = Series.objects.get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404
    return render(request, 'series.html', {
        'series': _series,
        'page_url': _get_url(request)
    })


def chapter(request, slug=None, vol=0, num=0, page=1):
    if page == 0:
        raise Http404
    chapters = {
        'all': Chapter.objects.filter(series__slug=slug),
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
    if page > all_pages.count():
        raise Http404
    return render(request, 'chapter.html', {
        'all_chapters': chapters['all'].reverse(),
        'curr_chapter': chapters['curr'],
        'next_chapter': chapters['next'],
        'prev_chapter': chapters['prev'],
        'all_pages': all_pages,
        'curr_page': all_pages.get(number=page),
        'page_url': _get_url(request)
    })


def chapter_redirect(request, slug=None, vol=0, num=0):
    return redirect('reader:chapter', permanent=True,
                    slug=slug, vol=vol, num=num, page=1)


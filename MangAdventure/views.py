from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control

from constance import config

from api.response import JsonError
from reader.models import Category, Chapter

from .utils.search import parse, query


def _error_context(msg, status=500):
    return {'error_message': msg, 'error_status': status}


def index(request):
    latest = Chapter.objects.prefetch_related('groups', 'series') \
        .order_by('-uploaded')[:config.MAX_RELEASES:1]
    return render(request, 'index.html', {'latest_releases': latest})


def search(request):
    results = None
    params = parse(request)
    if any(p in ('q', 'author', 'status') for p in request.GET):
        results = query(params)
        if len(results) == 1 and not results.first().chapters.count():
            results = None
    return render(request, 'search.html', {
        'query': params['query'],
        'author': params['author'],
        'status': params['status'],
        'in_categories': params['categories']['include'],
        'ex_categories': params['categories']['exclude'],
        'all_categories': Category.objects.all(),
        'results': results, 'total': len(results or '')
    })


@cache_control(public=True, max_age=2628000)
def opensearch(request):
    _icon = request.build_absolute_uri(
        settings.MEDIA_URL + config.FAVICON
    )
    _search = request.build_absolute_uri('/search/')
    _self = request.build_absolute_uri('/opensearch.xml')
    return render(
        request, 'opensearch.xml', {
            'search': _search, 'self': _self, 'icon': _icon,
        }, 'application/opesearchdescription+xml'
    )


@cache_control(public=True, max_age=31536000)
def contribute(request):
    return render(request, 'contribute.json', {}, 'application/json')


@cache_control(public=True, max_age=31536000)
def robots(request):
    return HttpResponse('User-agent: *\nDisallow:', 'text/plain')


def handler400(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Bad request', 400)
    context = _error_context(
        'The server could not understand the request.', 400
    )
    return render(request, template_name, context, status=400)


def handler403(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Forbidden', 403)
    context = _error_context(
        'You do not have permission to access this page.', 403
    )
    return render(request, template_name, context, status=403)


def handler404(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Invalid API endpoint', 501)
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name, context, status=404)


def handler500(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Internal server error')
    context = _error_context(  # Shrug
        'Whoops! Something went wrong. &macr;&#8726;_(&#12484;)_/&macr;'
    )
    return render(request, template_name, context, status=500)


def handler503(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Service unavailable', 503)
    context = _error_context(
        'The site is currently under maintenance.'
        ' Please try again later.', 503
    )
    return render(request, template_name, context, status=503)

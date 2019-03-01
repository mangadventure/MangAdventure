from django.shortcuts import render
from django.conf import settings
from constance import config
from reader.models import Category, Chapter
from api.response import JsonError
from .utils import search as s


def _error_context(msg, status=500):
    return {'error_message': msg, 'error_status': status}


def index(request):
    return render(request, 'index.html', {
        'latest_releases': Chapter.objects
                  .prefetch_related('groups', 'series')
                  .order_by('-uploaded')[:config.MAX_RELEASES:1]
    })


def info(request): return render(request, 'info.html', {})


def search(request):
    results = None
    params = s.parse(request)
    if any(p in ('q', 'author', 'status') for p in request.GET):
        results = s.query(params)
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


def opensearch(request):
    host = request.get_host()
    icon = request.build_absolute_uri(
        settings.MEDIA_URL + config.FAVICON)
    return render(request, 'opensearch.xml', context={
        'host': host, 'name': config.NAME, 'icon': icon,
        'url': '%s://%s' % (request.scheme, host)
    }, content_type='application/opesearchdescription+xml')


def handler400(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Bad request', 400)
    context = _error_context('The server could not '
                             'understand the request.', 400)
    return render(request, template_name=template_name,
                  context=context, status=400)


def handler403(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Forbidden', 403)
    context = _error_context("You don't have permission "
                             "to access this page.", 403)
    return render(request, template_name=template_name,
                  context=context, status=403)


def handler404(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Invalid API endpoint', 501)
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name=template_name,
                  context=context, status=404)


def handler500(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Internal server error', 500)
    context = _error_context('Whoops! Something went wrong.'
                             ' &macr;&#8726;_(&#12484;)_/&macr;')  # Shrug
    return render(request, template_name=template_name,
                  context=context, status=500)


def handler503(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return JsonError('Service unavailable', 503)
    context = _error_context('The server is currently under maintenance.'
                             ' Please try again later.', 503)
    return render(request, template_name=template_name,
                  context=context, status=503)


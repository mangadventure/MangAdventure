"""The main views and error handlers."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control

from api.response import JsonError
from reader.models import Category, Chapter

from .bad_bots import BOTS
from .search import parse, query

if TYPE_CHECKING:
    from django.http import HttpRequest


def _error_context(msg: str, status: int = 500) -> Dict[str, Any]:
    return {'error_message': msg, 'error_status': status}


def index(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the index page which shows the latest releases.

    :param request: The original request.

    :return: A response with the rendered ``index.html`` template.
    """
    latest = Chapter.objects.prefetch_related('groups', 'series') \
        .order_by('-uploaded')[:settings.CONFIG['MAX_RELEASES']:1]
    return render(request, 'index.html', {'latest_releases': latest})


def search(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves a page used for searching for series.

    :param request: The original request.

    :return: A response with the rendered ``search.html`` template.
    """
    results = None
    params = parse(request)
    if any(p in ('q', 'author', 'status') for p in request.GET):
        results = query(params)
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
def opensearch(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the ``opensearch.xml`` file.

    :param request: The original request.

    :return: A response with the rendered ``opensearch.xml`` template.
    """
    _icon = request.build_absolute_uri(
        settings.CONFIG['FAVICON']
    )
    _search = request.build_absolute_uri('/search/')
    _self = request.build_absolute_uri('/opensearch.xml')
    return render(
        request, 'opensearch.xml', {
            'name': settings.CONFIG['NAME'],
            'search': _search, 'self': _self, 'icon': _icon,
        }, 'application/opesearchdescription+xml'
    )


@cache_control(public=True, max_age=31536000)
def contribute(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the ``contribute.json`` file.

    :param request: The original request.

    :return: A response with the ``contribute.json`` file.
    """
    return render(request, 'contribute.json', {}, 'application/json')


@cache_control(public=True, max_age=2628000)
def robots(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the ``robots.txt`` file.

    :param request: The original request.

    :return: A response with the generated ``robots.txt`` file.
    """
    ctype = 'text/plain; charset=us-ascii'
    _robots = 'User-agent: *\nDisallow:\n\n' + '\n'.join(
        f'User-agent: {ua}\nDisallow: /\n' for ua in BOTS
    )
    return HttpResponse(content=_robots, content_type=ctype)


def handler400(request: 'HttpRequest', exception: Optional[Exception] = None,
               template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`400` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonError('Bad request', 400)
    context = _error_context(
        'The server could not understand the request.', 400
    )
    return render(request, template_name, context, status=400)


def handler403(request: 'HttpRequest', exception: Optional[Exception] = None,
               template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`403` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonError('Forbidden', 403)
    context = _error_context(
        'You do not have permission to access this page.', 403
    )
    return render(request, template_name, context, status=403)


def handler404(request: 'HttpRequest', exception: Optional[Exception] = None,
               template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`404` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonError('Invalid API endpoint', 501)
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name, context, status=404)


def handler500(request: 'HttpRequest', exception: Optional[Exception] = None,
               template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`500` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonError('Internal server error')
    context = _error_context(  # Shrug
        'Whoops! Something went wrong. &macr;&#8726;_(&#12484;)_/&macr;'
    )
    return render(request, template_name, context, status=500)


def handler503(request: 'HttpRequest', exception: Optional[Exception] = None,
               template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`503` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonError('Service unavailable', 503)
    context = _error_context(
        'The site is currently under maintenance.'
        ' Please try again later.', 503
    )
    return render(request, template_name, context, status=503)


__all__ = [
    'index', 'search', 'opensearch', 'contribute',
    'robots', 'handler400', 'handler403',
    'handler404', 'handler500', 'handler503'
]

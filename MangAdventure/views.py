"""The main views and error handlers."""

from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone as tz
from django.views.decorators.cache import cache_control

from api.response import JsonError
from reader.models import Category, Chapter

from .bad_bots import BOTS
from .jsonld import breadcrumbs
from .search import parse, query

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


def _error_context(msg: str, status: int = 500) -> Dict[str, Any]:
    return {'error_message': msg, 'error_status': status}


@cache_control(max_age=600, must_revalidate=True)
def index(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the index page which shows the latest releases.

    :param request: The original request.

    :return: A response with the rendered ``index.html`` template.
    """
    _max = settings.CONFIG['MAX_RELEASES']
    latest = Chapter.objects.prefetch_related('groups', 'series') \
        .filter(published__lte=tz.now()).order_by('-published')[:_max]
    uri = request.build_absolute_uri('/')
    crumbs = breadcrumbs([('Home', uri)])
    return render(request, 'index.html', {
        'latest_releases': latest, 'breadcrumbs': crumbs
    })


@cache_control(max_age=600, must_revalidate=True)
def search(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves a page used for searching for series.

    :param request: The original request.

    :return: A response with the rendered ``search.html`` template.
    """
    results = None
    params = parse(request)
    keys = {'q', 'author', 'status', 'categories'}
    if request.GET.keys() & keys:
        results = query(params).order_by('title')
    uri = request.build_absolute_uri(request.path)
    crumbs = breadcrumbs([('Search', uri)])
    return render(request, 'search.html', {
        'query': params.query,
        'author': params.author,
        'status': params.status,
        'in_categories': params.categories[0],
        'ex_categories': params.categories[1],
        'all_categories': Category.objects.all(),
        'results': results, 'total': len(results or ''),
        'breadcrumbs': crumbs
    })


@cache_control(public=True, max_age=2628000, immutable=True)
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


@cache_control(public=True, max_age=31536000, immutable=True)
def contribute(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the ``contribute.json`` file.

    :param request: The original request.

    :return: A response with the ``contribute.json`` file.
    """
    return render(request, 'contribute.json', {}, 'application/json')


@cache_control(public=True, max_age=2628000, immutable=True)
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


def handler400(request: 'HttpRequest', exception: Optional[Exception]
               = None, template_name: str = 'error.html'
               ) -> HttpResponse:  # pragma: no cover
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


def handler403(request: 'HttpRequest', exception: Optional[Exception]
               = None, template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`403` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):  # pragma: no cover
        return JsonError('Forbidden', 403)
    context = _error_context(
        'You do not have permission to access this page.', 403
    )
    return render(request, template_name, context, status=403)


def handler404(request: 'HttpRequest', exception: Optional[Exception]
               = None, template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`404` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~api.response.JsonError` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):  # pragma: no cover
        return JsonError('Invalid API endpoint', 501)
    if find_spec('sentry_sdk'):  # pragma: no cover
        from sentry_sdk import capture_message
        capture_message('Page not found', level='warning')
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name, context, status=404)


def handler500(request: 'HttpRequest', exception: Optional[Exception]
               = None, template_name: str = 'error.html'
               ) -> HttpResponse:  # pragma: no cover
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


__all__ = [
    'index', 'search', 'opensearch', 'contribute', 'robots',
    'handler400', 'handler403', 'handler404', 'handler500'
]

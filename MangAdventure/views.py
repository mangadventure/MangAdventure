"""The main views and error handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models import Prefetch
from django.db.models.functions import Now
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import escapejs
from django.views.decorators.cache import cache_control

from groups.models import Group
from reader.models import Category, Chapter

from .bad_bots import BOTS
from .jsonld import breadcrumbs
from .search import parse, query

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


def _error_context(msg: str, status: int = 500) -> dict[str, Any]:
    return {'error_message': msg, 'error_status': status}


@cache_control(public=True, max_age=600, stale_if_error=300)
def index(request: HttpRequest) -> HttpResponse:
    """
    View that serves the index page which shows the latest releases.

    :param request: The original request.

    :return: A response with the rendered ``index.html`` template.
    """
    max_: int = settings.CONFIG['MAX_RELEASES']
    groups = Group.objects.only('name')
    latest = Chapter.objects.filter(
        published__lte=Now(),
        series__licensed=False
    ).order_by('-published').only(
        'title', 'number', 'volume', 'final', 'published',
        'series__title', 'series__slug', 'series__format'
    ).prefetch_related(
        Prefetch('groups', queryset=groups)
    ).select_related('series')[:max_]
    uri = request.build_absolute_uri('/')
    crumbs = breadcrumbs([('Home', uri)])
    return render(request, 'index.html', {
        'breadcrumbs': crumbs,
        'latest_releases': latest
    })


@cache_control(public=True, max_age=600)
def search(request: HttpRequest) -> HttpResponse:
    """
    View that serves a page used for searching for series.

    :param request: The original request.

    :return: A response with the rendered ``search.html`` template.
    """
    results = []
    params = parse(request)
    if request.GET.keys() & {'q', 'author', 'status', 'categories'}:
        results = list(query(params).prefetch_related(
            'categories', 'authors', 'artists'
        ).exclude(licensed=True).order_by('title'))
    uri = request.build_absolute_uri(request.path)
    crumbs = breadcrumbs([('Search', uri)])
    categories = list(Category.objects.all())
    return render(request, 'search.html', {
        'query': params.query,
        'author': params.author,
        'status': params.status,
        'in_categories': params.categories[0],
        'ex_categories': params.categories[1],
        'all_categories': categories,
        'results': results,
        'breadcrumbs': crumbs
    })


@cache_control(public=True, max_age=2628000, immutable=True)
def opensearch(request: HttpRequest) -> HttpResponse:
    """
    View that serves the ``opensearch.xml`` file.

    :param request: The original request.

    :return: A response with the rendered ``opensearch.xml`` template.
    """
    icon = request.build_absolute_uri(settings.CONFIG['FAVICON'])
    search_ = request.build_absolute_uri('/search/')
    self_ = request.build_absolute_uri('/opensearch.xml')
    return render(
        request, 'opensearch.xml', {
            'name': settings.CONFIG['NAME'],
            'icon_type': settings.CONFIG['FAVICON_TYPE'],
            'icon': icon, 'search': search_, 'self': self_,
        }, 'application/opesearchdescription+xml'
    )


@cache_control(public=True, max_age=31536000, immutable=True)
def contribute(request: HttpRequest) -> HttpResponse:
    """
    View that serves the ``contribute.json`` file.

    :param request: The original request.

    :return: A response with the ``contribute.json`` file.
    """
    return render(request, 'contribute.json', {}, 'application/json')


@cache_control(public=True, max_age=2628000, immutable=True)
def manifest(request: HttpRequest) -> HttpResponse:
    """
    View that serves the ``manifest.webmanifest`` file.

    :param request: The original request.

    :return: A response with the ``manifest.webmanifest`` file.
    """
    return render(request, 'manifest.webmanifest', {
        'lang': settings.LANGUAGE_CODE,
        'name': escapejs(settings.CONFIG['NAME']),
        'description': escapejs(settings.CONFIG['DESCRIPTION']),
        'background': settings.CONFIG['MAIN_BG_COLOR'],
        'color': settings.CONFIG['MAIN_TEXT_COLOR'],
    }, 'application/manifest+json')


@cache_control(public=True, max_age=2628000, immutable=True)
def robots(request: HttpRequest) -> HttpResponse:
    """
    View that serves the ``robots.txt`` file.

    :param request: The original request.

    :return: A response with the generated ``robots.txt`` file.
    """
    ctype = 'text/plain; charset=us-ascii'
    robots_ = 'User-agent: *\nDisallow:\n\n' + '\n'.join(
        f'User-agent: {ua}\nDisallow: /\n' for ua in BOTS
    )
    return HttpResponse(content=robots_, content_type=ctype)


def handler400(request: HttpRequest, exception: Exception | None
               = None, template_name: str = 'error.html'
               ) -> HttpResponse:  # pragma: no cover
    """
    Handler for :status:`400` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~django.http.JsonResponse` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonResponse({'error': 'Bad request'}, status=400)
    context = _error_context(
        'The server could not understand the request.', 400
    )
    return render(request, template_name, context, status=400)


def handler403(request: HttpRequest, exception: Exception | None
               = None, template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`403` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~django.http.JsonResponse` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):  # pragma: no cover
        return JsonResponse({'error': 'Forbidden'}, status=403)
    context = _error_context(
        'You do not have permission to access this page.', 403
    )
    return render(request, template_name, context, status=403)


def handler404(request: HttpRequest, exception: Exception | None
               = None, template_name: str = 'error.html') -> HttpResponse:
    """
    Handler for :status:`404` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~django.http.JsonResponse` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):  # pragma: no cover
        return JsonResponse({'error': 'Invalid API endpoint'}, status=501)
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name, context, status=404)


def handler500(request: HttpRequest, exception: Exception | None
               = None, template_name: str = 'error.html'
               ) -> HttpResponse:  # pragma: no cover
    """
    Handler for :status:`500` responses.

    :param request: The original request.
    :param exception: The exception that occurred.
    :param template_name: The name of the error template.

    :return: A :class:`~django.http.JsonResponse` for API URLs,
             otherwise a response with the rendered error template.
    """
    if request.path.startswith('/api'):
        return JsonResponse({'error': 'Internal server error'}, status=500)
    context = _error_context(  # Shrug
        'Whoops! Something went wrong. &macr;&#8726;_(&#12484;)_/&macr;'
    )
    return render(request, template_name, context, status=500)


__all__ = [
    'index', 'search', 'opensearch', 'robots',
    'contribute', 'manifest', 'handler400',
    'handler403', 'handler404', 'handler500'
]

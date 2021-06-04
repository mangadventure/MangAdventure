"""The views of the api.v1 app."""

from typing import TYPE_CHECKING, Dict, Iterable, Optional

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone as tz
from django.utils.http import http_date
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import last_modified

from MangAdventure.search import get_response

from groups.models import Group, Member
from reader.models import Artist, Author, Category, Chapter, Series

from ..response import JsonError, require_methods_api

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime  # isort:skip
    from typing import Union  # isort:skip
    from django.http import HttpRequest  # isort:skip
    Person = Union[Author, Artist]


def _latest(request: 'HttpRequest', slug: Optional[str] = None,
            vol: Optional[int] = None, num: Optional[float] = None
            ) -> 'Optional[datetime]':
    try:
        if slug is None:
            q = Q(chapters__published__lte=tz.now())
            return Series.objects.only('modified').annotate(
                chapter_count=Count('chapters', filter=q)
            ).filter(q & Q(chapter_count__gt=0)).latest().modified
        if vol is None:
            return Series.objects.only('modified').filter(
                chapters__published__lte=tz.now(), slug=slug
            ).distinct().get().modified
        if num is None:
            return Chapter.objects.only('modified').filter(
                series__slug=slug, volume=vol, published__lte=tz.now()
            ).latest().modified
        return Chapter.objects.only('modified').filter(
            series__slug=slug, volume=vol,
            number=num, published__lte=tz.now()
        ).latest().modified
    except ObjectDoesNotExist:
        return None


def _chapter_response(request: 'HttpRequest', _chapter: Chapter) -> Dict:
    url = request.build_absolute_uri(_chapter.get_absolute_url())
    return {
        'url': url,
        'title': _chapter.title,
        'full_title': str(_chapter),
        'pages_root': url.replace('/reader/', f'{settings.MEDIA_URL}series/'),
        'pages_list': [p._file_name for p in _chapter.pages.iterator()],
        'date': http_date(_chapter.published.timestamp()),
        'final': _chapter.final,
        'groups': list(_chapter.groups.values('id', 'name'))
    }


def _volume_response(request: 'HttpRequest',
                     chapters: Iterable[Chapter]) -> Dict:
    return {
        f'{c.number:g}': _chapter_response(request, c)
        for c in chapters
    }


def _series_response(request: 'HttpRequest', _series: Series) -> Dict:
    response = {
        'slug': _series.slug,
        'title': _series.title,
        'aliases': _series.aliases.names(),
        'url': request.build_absolute_uri(_series.get_absolute_url()),
        'description': _series.description,
        'authors': [],
        'artists': [],
        'categories': list(
            _series.categories.values('name', 'description')
        ),
        'cover': request.build_absolute_uri(_series.cover.url),
        'completed': _series.completed,
        'volumes': {},
    }
    chapters = _series.chapters.filter(published__lte=tz.now())
    for _chapter in chapters:
        if _chapter.volume not in response['volumes']:
            response['volumes'][_chapter.volume] = _volume_response(
                request, chapters.filter(volume=_chapter.volume)
            )
    for _author in _series.authors.prefetch_related('aliases').iterator():
        response['authors'].append([_author.name, *_author.aliases.names()])
    for _artist in _series.artists.prefetch_related('aliases').iterator():
        response['artists'].append([_artist.name, *_artist.aliases.names()])
    return response


def _person_response(request: 'HttpRequest', _person: 'Person') -> Dict:
    response = {
        'id': _person.id,
        'name': _person.name,
        'aliases': _person.aliases.names(),
        'series': [],
    }
    for _series in _person.series_set.prefetch_related('aliases').iterator():
        response['series'].append({
            'slug': _series.slug,
            'title': _series.title,
            'aliases': _series.aliases.names(),
        })
    return response


def _member_response(request: 'HttpRequest', _member: Member) -> Dict:
    return {
        'id': _member.id,
        'name': _member.name,
        'roles': [r.get_role_display() for r in _member.roles.iterator()],
        'twitter': _member.twitter,
        'discord': _member.discord,
    }


def _group_response(request: 'HttpRequest', _group: Group) -> Dict:
    logo = ''
    if _group.logo:
        logo = request.build_absolute_uri(_group.logo.url)
    response = {
        'id': _group.id,
        'name': _group.name,
        'description': _group.description,
        'website': _group.website,
        'discord': _group.discord,
        'twitter': _group.twitter,
        'logo': logo,
        'members': [
            _member_response(request, m) for m
            in _group.members.distinct().iterator()
        ],
        'series': [],
    }
    _series = []
    for _chapter in _group.releases.prefetch_related('series__aliases') \
            .filter(published__lte=tz.now()).iterator():
        if _chapter.series_id not in _series:
            response['series'].append({
                'slug': _chapter.series.slug,
                'title': _chapter.series.title,
                'aliases': _chapter.series.aliases.names()
            })
            _series.append(_chapter.series_id)
    return response


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
@cache_control(public=True, max_age=600, must_revalidate=True)
def all_releases(request: 'HttpRequest') -> JsonResponse:
    """
     View that serves all the releases in a JSON array.

    :param request: The original request.

    :return: A JSON-formatted response with the releases.
    """
    response = []
    q = Q(chapters__published__lte=tz.now())
    _series = Series.objects.annotate(
        chapter_count=Count('chapters', filter=q)
    ).filter(q & Q(chapter_count__gt=0))
    for s in _series.prefetch_related('chapters').iterator():
        series_res = {
            'slug': s.slug,
            'title': s.title,
            'url': request.build_absolute_uri(s.get_absolute_url()),
            'cover': request.build_absolute_uri(s.cover.url),
            'latest_chapter': {},
        }
        try:
            series_res['latest_chapter'] = s.chapters.values(
                'title', 'volume', 'number', 'published'
            ).latest()
        except ObjectDoesNotExist:
            pass
        else:
            series_res['latest_chapter']['date'] = http_date(
                series_res['latest_chapter'].pop('published').timestamp()
            )
        response.append(series_res)
    return JsonResponse(response, safe=False)


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
@cache_control(public=True, max_age=600, must_revalidate=True)
def all_series(request: 'HttpRequest') -> JsonResponse:
    """
     View that serves all the series in a JSON array.

    :param request: The original request.

    :return: A JSON-formatted response with the series.
    """
    return JsonResponse([
        _series_response(request, s)
        for s in get_response(request)
    ], safe=False)


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
@cache_control(public=True, max_age=600, must_revalidate=True)
def series(request: 'HttpRequest', slug: str) -> JsonResponse:
    """
     View that serves a single series as a JSON object.

    :param request: The original request.
    :param slug: The slug of the series.

    :return: A JSON-formatted response with the series.
    """
    try:
        _series = Series.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_series_response(request, _series))


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
@cache_control(public=True, max_age=600, must_revalidate=True)
def volume(request: 'HttpRequest', slug: str, vol: int) -> JsonResponse:
    """
     View that serves a single volume as a JSON object.

    :param request: The original request.
    :param slug: The slug of the series.
    :param vol: The number of the volume.

    :return: A JSON-formatted response with the volume.
    """
    try:
        _series = Series.objects \
            .prefetch_related('chapters__pages').get(slug=slug)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    chapters = _series.chapters.filter(volume=vol, published__lte=tz.now())
    if not chapters:
        return JsonError('Not found', 404)
    return JsonResponse(_volume_response(request, chapters))


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
@cache_control(public=True, max_age=600, must_revalidate=True)
def chapter(request: 'HttpRequest', slug: str,
            vol: int, num: float) -> JsonResponse:
    """
     View that serves a single chapter as a JSON object.

    :param request: The original request.
    :param slug: The slug of the series.
    :param vol: The number of the volume.
    :param num: The number of the chapter.

    :return: A JSON-formatted response with the chapter.
    """
    try:
        _chapter = Chapter.objects.prefetch_related('pages').get(
            series__slug=slug, volume=vol,
            number=num, published__lte=tz.now()
        )
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_chapter_response(request, _chapter))


def _is_author(request: 'HttpRequest') -> bool:
    return request.path[:16] == '/api/v1/authors'


@csrf_exempt
@require_methods_api()
@cache_control(public=True, max_age=1800, must_revalidate=True)
def all_people(request: 'HttpRequest') -> JsonResponse:
    """
     View that serves all the authors/artists in a JSON array.

    :param request: The original request.

    :return: A JSON-formatted response with the authors/artists.
    """
    _type = Author if _is_author(request) else Artist
    return JsonResponse([
        _person_response(request, p) for p in
        _type.objects.prefetch_related(
            'aliases', 'series_set__aliases'
        ).iterator()
    ], safe=False)


@csrf_exempt
@require_methods_api()
@cache_control(public=True, max_age=1800, must_revalidate=True)
def person(request: 'HttpRequest', p_id: int) -> JsonResponse:
    """
     View that serves a single author/artist as a JSON object.

    :param request: The original request.
    :param p_id: The ID of the author/artist.

    :return: A JSON-formatted response with the author/artist.
    """
    try:
        _type = Author if _is_author(request) else Artist
        _person = _type.objects.prefetch_related(
            'aliases', 'series_set__aliases'
        ).get(id=p_id)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_person_response(request, _person))


@csrf_exempt
@require_methods_api()
@cache_control(public=True, max_age=1800, must_revalidate=True)
def all_groups(request: 'HttpRequest') -> JsonResponse:
    """
     View that serves all the groups in a JSON array.

    :param request: The original request.

    :return: A JSON-formatted response with the groups.
    """
    return JsonResponse([
        _group_response(request, g) for g in
        Group.objects.prefetch_related(
            'releases__series', 'roles__member'
        ).iterator()
    ], safe=False)


@csrf_exempt
@require_methods_api()
@cache_control(public=True, max_age=1800, must_revalidate=True)
def group(request: 'HttpRequest', g_id: int) -> JsonResponse:
    """
     View that serves a single group as a JSON object.

    :param request: The original request.
    :param g_id: The ID of the group.

    :return: A JSON-formatted response with the group.
    """
    try:
        _group = Group.objects.prefetch_related(
            'releases__series', 'roles__member'
        ).get(id=g_id)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_group_response(request, _group))


@csrf_exempt
@require_methods_api()
@cache_control(public=True, max_age=1800, must_revalidate=True)
def categories(request: 'HttpRequest') -> JsonResponse:
    """
     View that serves all the categories in a JSON array.

    :param request: The original request.

    :return: A JSON-formatted response with the categories.
    """
    return JsonResponse(list(Category.objects.values()), safe=False)


@csrf_exempt
@require_methods_api()
def invalid_endpoint(request: 'HttpRequest') -> JsonError:
    """
     View that serves a :status:`501` error as a JSON object.

    :param request: The original request.

    :return: A JSON-formatted response with the error.
    """
    return JsonError('Invalid API endpoint', 501)


__all__ = [
    'all_releases', 'all_series', 'series', 'volume',
    'chapter', 'all_people', 'person', 'all_groups',
    'group', 'categories', 'invalid_endpoint'
]

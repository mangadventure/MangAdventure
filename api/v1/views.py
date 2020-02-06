"""The views of the api.v1 app."""

from typing import TYPE_CHECKING, Dict, Iterable, Optional

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import last_modified

from MangAdventure.search import get_response

from groups.models import Group, Member
from reader.models import Artist, Author, Category, Chapter, Series

from ..response import JsonError, require_methods_api

if TYPE_CHECKING:  # pragma: no cover
    from typing import Union
    from django.db.models import DateTimeField  # noqa: F401
    from django.http import HttpRequest
    Person = Union[Author, Artist]


def _latest(request: 'HttpRequest', slug: Optional[str] = None,
            vol: Optional[int] = None, num: Optional[float] = None
            ) -> Optional['DateTimeField']:
    try:
        if slug is None:
            return Series.objects.only('modified').latest().modified
        if vol is None:
            return Series.objects.only('modified').get(slug=slug).modified
        if num is None:
            return Chapter.objects.only('modified').filter(
                series__slug=slug, volume=vol
            ).latest().modified
        return Chapter.objects.only('modified').filter(
            series__slug=slug, volume=vol, number=num
        ).latest().modified
    except ObjectDoesNotExist:
        return None


def _chapter_response(request: 'HttpRequest', _chapter: Chapter) -> Dict:
    url = request.build_absolute_uri(_chapter.get_absolute_url())
    return {
        'title': _chapter.title,
        'url': url,
        'pages_root': url.replace('/reader/', f'{settings.MEDIA_URL}series/'),
        'pages_list': [p._file_name for p in _chapter.pages.all()],
        'date': _chapter.uploaded_date,
        'final': _chapter.final,
        'groups': [
            {'id': _group.id, 'name': _group.name}
            for _group in _chapter.groups.all()
        ]
    }


def _volume_response(request: 'HttpRequest',
                     chapters: Iterable[Chapter]) -> Dict:
    response = {}
    for _chapter in chapters:
        response[f'{_chapter.number:g}'] = \
            _chapter_response(request, _chapter)
    return response


def _series_response(request: 'HttpRequest', _series: Series) -> Dict:
    response = {
        'slug': _series.slug,
        'title': _series.title,
        'aliases': [a.alias for a in _series.aliases.all()],
        'url': request.build_absolute_uri(_series.get_absolute_url()),
        'description': _series.description,
        'authors': [],
        'artists': [],
        'categories': [],
        'cover': request.build_absolute_uri(_series.cover.url),
        'completed': _series.completed,
        'volumes': {},
    }
    for _chapter in _series.chapters.all():
        if _chapter.volume not in response['volumes']:
            response['volumes'][_chapter.volume] = _volume_response(
                request, _series.chapters.filter(volume=_chapter.volume)
            )
    for _author in _series.authors.all():
        names = [a.alias for a in _author.aliases.all()]
        names.insert(0, _author.name)
        response['authors'].append(names)
    for _artist in _series.artists.all():
        names = [a.alias for a in _artist.aliases.all()]
        names.insert(0, _artist.name)
        response['artists'].append(names)
    for _category in _series.categories.all():
        response['categories'].append({
            'name': _category.name,
            'description': _category.description
        })
    return response


def _person_response(request: 'HttpRequest', _person: 'Person') -> Dict:
    response = {
        'id': _person.id,
        'name': _person.name,
        'aliases': [a.alias for a in _person.aliases.all()],
        'series': [],
    }
    for _series in _person.series_set.all():
        response['series'].append({
            'slug': _series.slug,
            'title': _series.title,
            'aliases': [a.alias for a in _series.aliases.all()],
        })
    return response


def _member_response(request: 'HttpRequest', _member: Member) -> Dict:
    return {
        'id': _member.id,
        'name': _member.name,
        'roles': [r.get_role_display() for r in _member.roles.all()],
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
            _member_response(request, m)
            for m in _group.members.distinct()
        ],
        'series': [],
    }
    _series = []
    for _chapter in _group.releases.all():
        if _chapter.series.id not in _series:
            response['series'].append({
                'slug': _chapter.series.slug,
                'title': _chapter.series.title,
                'aliases': [a.alias for a in _chapter.series.aliases.all()]
            })
            _series.append(_chapter.series.id)
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
    _series = Series.objects.prefetch_related('chapters').all()
    response = []
    for s in _series:
        series_res = {
            'slug': s.slug,
            'title': s.title,
            'url': request.build_absolute_uri(s.get_absolute_url()),
            'cover': request.build_absolute_uri(s.cover.url),
            'latest_chapter': {},
        }
        try:
            last_chapter = s.chapters.latest()
            series_res['latest_chapter'] = {
                'title': last_chapter.title,
                'volume': last_chapter.volume,
                'number': last_chapter.number,
                'date': last_chapter.uploaded_date,
            }
        except ObjectDoesNotExist:
            pass
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
    chapters = _series.chapters.filter(volume=vol)
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
        _chapter = Chapter.objects.prefetch_related('pages') \
            .get(series__slug=slug, volume=vol, number=num)
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
    prefetch = ('aliases', 'series_set__aliases')
    _type = Author if _is_author(request) else Artist
    people = _type.objects.prefetch_related(*prefetch).all()
    response = [_person_response(request, p) for p in people]
    return JsonResponse(response, safe=False)


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
    prefetch = ('aliases', 'series_set__aliases')
    try:
        _type = Author if _is_author(request) else Artist
        _person = _type.objects.prefetch_related(*prefetch).get(id=p_id)
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
    prefetch = ('releases__series', 'roles__member')
    _groups = Group.objects.prefetch_related(*prefetch).all()
    response = [_group_response(request, g) for g in _groups]
    return JsonResponse(response, safe=False)


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
    prefetch = ('releases__series', 'roles__member')
    try:
        _group = Group.objects.prefetch_related(*prefetch).get(id=g_id)
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
    values = list(Category.objects.values())
    return JsonResponse(values, safe=False)


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

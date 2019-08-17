from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import last_modified

from api.response import JsonError, JsonResponse, require_methods_api
from groups.models import Group, Member
from MangAdventure.utils.search import get_response
from reader.models import Artist, Author, Category, Chapter, Series


def _chapter_response(request, _chapter):
    url = request.build_absolute_uri(_chapter.get_absolute_url())
    response = {
        'title': _chapter.title,
        'url': url,
        'pages_root': url.replace(
            '/reader', '%s%s' % (settings.MEDIA_URL, 'series')
        ),
        'pages_list': [p.get_file_name() for p in _chapter.pages.all()],
        'date': _chapter.uploaded_date,
        'final': _chapter.final,
        'groups': []
    }
    for _group in _chapter.groups.all():
        response['groups'].append({
            'id': _group.id,
            'name': _group.name,
        })
    return response


def _volume_response(request, _series, vol):
    response = {}
    chapters = _series.chapters.filter(volume=vol)
    if chapters.count() == 0:
        return JsonError('Not found', 404)
    for _chapter in chapters:
        response['%g' % _chapter.number] = \
            _chapter_response(request, _chapter)
    return response


def _series_response(request, _series):
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
            response['volumes'][_chapter.volume] = \
                _volume_response(request, _series, _chapter.volume)
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


def _person_response(request, _person):
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


def _member_response(request, _member):
    return {
        'id': _member.id,
        'name': _member.name,
        'roles': [r.get_role_display() for r in _member.roles.all()],
        'twitter': _member.twitter,
        'discord': _member.discord,
    }


def _group_response(request, _group):
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
        'members': [],
        'series': [],
    }
    member_ids = _group.roles.values_list(
        'member_id', flat=True
    ).distinct()
    for m_id in member_ids:
        response['members'].append(_member_response(
            request, Member.objects.get(id=m_id)
        ))
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
@last_modified(lambda request: Series.objects.latest().modified)
def all_releases(request):
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


def _latest(request, slug=None, vol=None, num=None):
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


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
def all_series(request):
    response = [
        _series_response(request, s)
        for s in get_response(request)
    ]
    return JsonResponse(response, safe=False)


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
def series(request, slug):
    try:
        _series = Series.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_series_response(request, _series))


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
def volume(request, slug, vol):
    try:
        vol = int(vol)
        if vol < 0:
            raise ValueError
        _series = Series.objects \
            .prefetch_related('chapters__pages').get(slug=slug)
    except (ValueError, TypeError):
        return JsonError('Bad request', 400)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_volume_response(request, _series, vol))


@csrf_exempt
@require_methods_api()
@last_modified(_latest)
def chapter(request, slug, vol, num):
    try:
        vol, num = int(vol), float(num)
        if vol < 0 or num < 0:
            raise ValueError
        _chapter = Chapter.objects.prefetch_related('pages') \
            .get(series__slug=slug, volume=vol, number=num)
    except (ValueError, TypeError):
        return JsonError('Bad request', 400)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_chapter_response(request, _chapter))


def _is_author(request):
    return request.path.startswith('/api/v1/authors')


@csrf_exempt
@require_methods_api()
def all_people(request):
    prefetch = ('aliases', 'series_set__aliases')
    _type = Author if _is_author(request) else Artist
    people = _type.objects.prefetch_related(*prefetch).all()
    response = [_person_response(request, p) for p in people]
    return JsonResponse(response, safe=False)


@csrf_exempt
@require_methods_api()
def person(request, p_id):
    prefetch = ('aliases', 'series_set__aliases')
    try:
        p_id = int(p_id)
        if p_id < 1:
            raise ValueError
        _type = Author if _is_author(request) else Artist
        _person = _type.objects.prefetch_related(*prefetch).get(id=p_id)
    except (ValueError, TypeError):
        return JsonError('Bad request', 400)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_person_response(request, _person))


@csrf_exempt
@require_methods_api()
def all_groups(request):
    prefetch = ('releases__series', 'roles__member')
    _groups = Group.objects.prefetch_related(*prefetch).all()
    response = [_group_response(request, g) for g in _groups]
    return JsonResponse(response, safe=False)


@csrf_exempt
@require_methods_api()
def group(request, g_id):
    prefetch = ('releases__series', 'roles__member')
    try:
        g_id = int(g_id)
        if g_id < 1:
            raise ValueError
        _group = Group.objects.prefetch_related(*prefetch).get(id=g_id)
    except (ValueError, TypeError):
        return JsonError('Bad request', 400)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return JsonResponse(_group_response(request, _group))


@csrf_exempt
@require_methods_api()
def categories(request):
    values = list(Category.objects.values())
    return JsonResponse(values, safe=False)


@csrf_exempt
@require_methods_api()
def invalid_endpoint(request):
    return JsonError('Invalid API endpoint', 501)

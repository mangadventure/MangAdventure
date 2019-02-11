from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import last_modified
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import http_date
from django.conf import settings
from django.urls import reverse
from time import mktime
from reader.models import Chapter, Series, Author, Artist, Category
from api.response import JsonVaryAllowResponse, JsonError
from MangAdventure.utils.search import get_response
from groups.models import Group, Member


def _chapter_response(request, _chapter, json=True):
    url = request.build_absolute_uri(_chapter.url)
    response = {
        'title': _chapter.title,
        'url': url,
        'pages_root': url.replace(
            '/reader', '%s%s' % (settings.MEDIA_URL, 'series')
        ),
        'pages_list': [p.image.url.split('/')[-1]
                       for p in _chapter.pages.all()],
        'date': http_date(mktime(_chapter.uploaded.timetuple())),
        'final': _chapter.final,
        'groups': []
    }
    for _group in _chapter.groups.all():
        response['groups'].append({
            'id': _group.id,
            'name': _group.name,
        })
    return JsonVaryAllowResponse(response) if json else response


def _volume_response(request, _series, vol, json=True):
    response = {}
    chapters = _series.chapters.filter(volume=vol)
    if chapters.count() == 0:
        return JsonError('Not found', 404)
    for _chapter in chapters:
        response['%g' % _chapter.number] = _chapter_response(
            request, _chapter, json=False)
    return JsonVaryAllowResponse(response) if json else response


def _series_response(request, _series, json=True):
    response = {
        'slug': _series.slug,
        'title': _series.title,
        'aliases': [a.alias for a in _series.aliases.all()],
        'url': request.build_absolute_uri(
            reverse('reader:series', args={_series.slug})
        ),
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
                request, _series, _chapter.volume, json=False
            )
    for _author in _series.authors.all():
        names = [_author.name]
        for alias in _author.aliases.all():
            names.append(alias.alias)
        response['authors'].append(names)
    for _artist in _series.artists.all():
        names = [_artist.name]
        for alias in _artist.aliases.all():
            names.append(alias.alias)
        response['artists'].append(names)
    for _category in _series.categories.all():
        response['categories'].append({
            'name': _category.name,
            'description': _category.description
        })
    return JsonVaryAllowResponse(response) if json else response


def _person_response(request, _person, json=True):
    response = {
        'id': _person.id,
        'name': _person.name,
        'aliases': [],
        'series': [],
    }
    for alias in _person.aliases.all():
        response['aliases'].append(alias.alias)
    for _series in _person.series_set.all():
        aliases = []
        for alias in _series.aliases.all():
            aliases.append(alias.alias)
        response['series'].append({
            'slug': _series.slug,
            'title': _series.title,
            'aliases': aliases,
        })
    return JsonVaryAllowResponse(response) if json else response


def _member_response(request, _member, json=True):
    response = {
        'id': _member.id,
        'name': _member.name,
        'roles': [],
        'twitter': _member.twitter,
        'discord': _member.discord,
    }
    for role in _member.roles.all():
        response['roles'].append(role.get_role_display())
    return JsonVaryAllowResponse(response) if json else response


def _group_response(request, _group, json=True):
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
    for role in _group.roles.values('member_id').distinct():
        _member = Member.objects.get(id=role['member_id'])
        response['members'].append(
            _member_response(request, _member, json=False)
        )
    _series = []
    for _chapter in _group.releases.all():
        if _chapter.series.title not in _series:
            response['series'].append({
                'slug': _chapter.series.slug,
                'title': _chapter.series.title,
                'aliases': [],
            })
            for alias in _chapter.series.aliases.all():
                response['series'][-1]['aliases'].append(alias.alias)
            _series.append(_chapter.series.title)
    return JsonVaryAllowResponse(response) if json else response


@csrf_exempt
@last_modified(lambda request: Series.objects.latest().modified)
def all_releases(request):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    _series = Series.objects.prefetch_related('chapters').all()
    response = []
    for s in _series:
        series_res = {
            'slug': s.slug,
            'title': s.title,
            'url': request.build_absolute_uri(
                reverse('reader:series', args={s.slug})),
            'cover': request.build_absolute_uri(s.cover.url),
            'latest_chapter': {},
        }
        try:
            last_chapter = s.chapters.latest()
            series_res['latest_chapter'] = {
                'title': last_chapter.title,
                'volume': last_chapter.volume,
                'number': last_chapter.number,
                'date': http_date(last_chapter.uploaded.timestamp()),
            }
        except ObjectDoesNotExist:
            pass
        response.append(series_res)
    return JsonVaryAllowResponse(response, safe=False)


def _latest(request, slug=None, vol=None, num=None):
    try:
        if slug is None:
            return Series.objects.latest().modified
        if vol is None:
            return Series.objects.get(slug=slug).modified
        if num is None:
            return Chapter.objects.filter(
                series_id=slug, volume=vol
            ).latest().modified
        return Chapter.objects.filter(
            series_id=slug, volume=vol, number=num
        ).latest().modified
    except ObjectDoesNotExist:
        return None


@csrf_exempt
@last_modified(_latest)
def all_series(request):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    response = []
    for s in get_response(request):
        response.append(_series_response(request, s, json=False))
    return JsonVaryAllowResponse(response, safe=False)


@csrf_exempt
@last_modified(_latest)
def series(request, slug):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    prefetch = ('aliases', 'authors', 'artists', 'categories')
    try:
        _series = Series.objects.prefetch_related(*prefetch).get(slug=slug)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return _series_response(request, _series)


@csrf_exempt
@last_modified(_latest)
def volume(request, slug, vol):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
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
    return _volume_response(request, _series, vol)


@csrf_exempt
@last_modified(_latest)
def chapter(request, slug, vol, num):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    try:
        vol, num = int(vol), float(num)
        if vol < 0 or num < 0:
            raise ValueError
        _chapter = Chapter.objects.prefetch_related('pages') \
            .get(series_id=slug, volume=vol, number=num)
    except (ValueError, TypeError):
        return JsonError('Bad request', 400)
    except ObjectDoesNotExist:
        return JsonError('Not found', 404)
    return _chapter_response(request, _chapter)


def _is_author(request):
    return request.path.startswith('/api/v1/authors')


@csrf_exempt
def all_people(request):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    prefetch = ('aliases', 'series_set__aliases')
    _type = Author if _is_author(request) else Artist
    people = _type.objects.prefetch_related(*prefetch).all()
    response = []
    for _person in people:
        response.append(_person_response(request, _person, json=False))
    return JsonVaryAllowResponse(response, safe=False)


@csrf_exempt
def person(request, p_id):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
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
    return _person_response(request, _person)


@csrf_exempt
def all_groups(request):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    prefetch = ('releases__series', 'roles__member')
    _groups = Group.objects.prefetch_related(*prefetch).all()
    response = []
    for g in _groups:
        response.append(_group_response(request, g, json=False))
    return JsonVaryAllowResponse(response, safe=False)


@csrf_exempt
def group(request, g_id):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
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
    return _group_response(request, _group)


@csrf_exempt
def categories(request):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    values = list(Category.objects.values())
    return JsonVaryAllowResponse(values, safe=False)


@csrf_exempt
def invalid_endpoint(request):
    if request.method not in ['GET', 'HEAD']:
        return JsonError('Method not allowed', 405)
    return JsonError('Invalid API endpoint', 501)


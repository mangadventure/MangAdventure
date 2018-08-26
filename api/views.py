from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from reader.models import Chapter, Series, Author, Artist


def json_error(message, status=500):
    return JsonResponse({'error': message, 'status': status}, status=status)


def _chapter_response(request, _chapter, json=True):
    response = {
        'title': _chapter.title,
        'url': request.build_absolute_uri(
            reverse('reader:chapter',
                    args=[_chapter.series.slug,
                          _chapter.volume,
                          _chapter.number])),
        'pages': [request.build_absolute_uri(page.image.url)
                  for page in _chapter.pages.all()],
        'date': _chapter.date,
        'final': _chapter.final,
    }
    return JsonResponse(response) if json else response


def _volume_response(request, _series, vol, json=True):
    response = {}
    chapters = _series.chapters.filter(volume=vol)
    if chapters.count() == 0:
        return json_error('Not found', 404)
    for _chapter in chapters:
        response[_chapter.number] = _chapter_response(
            request, _chapter, json=False)
    return JsonResponse(response) if json else response


def _series_response(request, _series, json=True):
    response = {
        'title': _series.title,
        'aliases': [a.alias for a in _series.aliases.all()],
        'url': request.build_absolute_uri(
            reverse('reader:series', args={_series.slug})),
        'description': _series.description,
        'authors': [],
        'artists': [],
        'cover': request.build_absolute_uri(_series.cover.url),
        'volumes': {},
        'completed': _series.completed,
    }
    for _chapter in _series.chapters.all():
        if _chapter.volume not in response['volumes']:
            response['volumes'][_chapter.volume] = _volume_response(
                request, _series, _chapter.volume, json=False)
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
    return JsonResponse(response) if json else response


def _author_response(request, _author, json=True):
    response = {
        'name': _author.name,
        'aliases': [],
        'series': {},
        'id': _author.id,
    }
    for alias in _author.aliases.all():
        response['aliases'].append(alias.alias)
    for _series in _author.series_set.all():
        response['series'][_series.slug] = {
            'title': _series.title,
            'aliases': [],
        }
        for alias in _series.aliases.all():
            response['series'][_series.slug]['aliases'].append(alias.alias)
    return JsonResponse(response) if json else response


def _artist_response(request, _artist, json=True):
    response = {
        'name': _artist.name,
        'aliases': [],
        'series': {},
        'id': _artist.id,
    }
    for alias in _artist.aliases.all():
        response['aliases'].append(alias.alias)
    for _series in _artist.series_set.all():
        response['series'][_series.slug] = {
            'title': _series.title,
            'aliases': [],
        }
        for alias in _series.aliases.all():
            response['series'][_series.slug]['aliases'].append(alias.alias)
    return JsonResponse(response) if json else response


@csrf_exempt
def all_releases(request):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    _series = Series.objects.all()
    response = {}
    for s in _series:
        last_chapter = s.chapters.last()
        response[s.slug] = {
            'title': s.title,
            'url': request.build_absolute_uri(
                reverse('reader:series', args={s.slug})),
            'cover': request.build_absolute_uri(s.cover.url),
            'latest_chapter': {},
        }
        if last_chapter:
            response[s.slug]['latest_chapter'] = {
                'title': last_chapter.title,
                'volume': last_chapter.volume,
                'number': last_chapter.number,
                'date': last_chapter.date,
            }
    return JsonResponse(response)


@csrf_exempt
def all_series(request):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    _series = Series.objects.all()
    response = {}
    for s in _series:
        response[s.slug] = _series_response(request, s)
    return JsonResponse(response)


@csrf_exempt
def series(request, slug=None):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    try:
        _series = Series.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _series_response(request, _series)


@csrf_exempt
def volume(request, slug=None, vol=0):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    try:
        vol = int(vol)
        if vol < 0:
            raise ValueError
    except (ValueError, TypeError):
        return json_error('Bad request', 400)
    try:
        _series = Series.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _volume_response(request, _series, vol)


@csrf_exempt
def chapter(request, slug=None, vol=0, num=0):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    try:
        vol, num = int(vol), int(num)
        if vol < 0 or num < 0:
            raise ValueError
    except (ValueError, TypeError):
        return json_error('Bad request', 400)
    try:
        _chapter = Chapter.objects.get(series__slug=slug,
                                       volume=vol, number=num)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _chapter_response(request, _chapter)


@csrf_exempt
def all_authors(request):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    authors = Author.objects.all()
    response = []
    for _author in authors:
        response.append(_author_response(request, _author, json=False))
    return JsonResponse(response, safe=False)


@csrf_exempt
def author(request, auth_id=0):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    try:
        auth_id = int(auth_id)
        if auth_id < 1:
            raise ValueError
    except (ValueError, TypeError):
        return json_error('Bad request', 400)
    try:
        _author = Author.objects.get(id=auth_id)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _author_response(request, _author)


@csrf_exempt
def all_artists(request):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    artists = Artist.objects.all()
    response = []
    for _artist in artists:
        response.append(_artist_response(request, _artist, json=False))
    return JsonResponse(response, safe=False)


@csrf_exempt
def artist(request, art_id=0):
    if request.method != 'GET':
        return json_error('Method not allowed', 405)
    try:
        art_id = int(art_id)
        if art_id < 1:
            raise ValueError
    except (ValueError, TypeError):
        return json_error('Bad request', 400)
    try:
        _artist = Artist.objects.get(id=art_id)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _artist_response(request, _artist)


@csrf_exempt
def invalid_endpoint(request):
    return json_error('Invalid API endpoint', 501)


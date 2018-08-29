from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import last_modified
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import http_date
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
        'pages': [p.image.url.split('/')[-1] for p in _chapter.pages.all()],
        'date': http_date(_chapter.uploaded.timestamp()),
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
        'slug': _series.slug,
        'title': _series.title,
        'aliases': [a.alias for a in _series.aliases.all()],
        'url': request.build_absolute_uri(
            reverse('reader:series', args={_series.slug})),
        'description': _series.description,
        'authors': [],
        'artists': [],
        'cover': request.build_absolute_uri(_series.cover.url),
        'completed': _series.completed,
        'volumes': {},
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
    return JsonResponse(response) if json else response


@csrf_exempt
@last_modified(lambda request: Series.objects.latest().modified)
def all_releases(request):
    if request.method not in ['GET', 'HEAD']:
        return json_error('Method not allowed', 405)
    _series = Series.objects.all()
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
    return JsonResponse(response, safe=False)


@csrf_exempt
@last_modified(lambda request: Series.objects.latest().modified)
def all_series(request):
    if request.method not in ['GET', 'HEAD']:
        return json_error('Method not allowed', 405)
    _series = Series.objects.all()
    response = []
    for s in _series:
        response.append(_series_response(request, s, json=False))
    return JsonResponse(response, safe=False)


@csrf_exempt
@last_modified(lambda request, slug: Series.objects.get(slug=slug).modified)
def series(request, slug=None):
    if request.method not in ['GET', 'HEAD']:
        return json_error('Method not allowed', 405)
    try:
        _series = Series.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _series_response(request, _series)


@csrf_exempt
@last_modified(lambda request, slug, vol: Chapter.objects.filter(
    series__slug=slug, volume=vol).latest().modified)
def volume(request, slug=None, vol=0):
    if request.method not in ['GET', 'HEAD']:
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
@last_modified(lambda request, slug, vol, num: Chapter.objects.filter(
    series__slug=slug, volume=vol, number=num).latest().modified)
def chapter(request, slug=None, vol=0, num=0):
    if request.method not in ['GET', 'HEAD']:
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
def all_people(request):
    if request.method not in ['GET', 'HEAD']:
        return json_error('Method not allowed', 405)
    if request.path.startswith('/api/authors'):
        people = Author.objects.all()
    else:
        people = Artist.objects.all()
    response = []
    for _person in people:
        response.append(_person_response(request, _person, json=False))
    return JsonResponse(response, safe=False)


@csrf_exempt
def person(request, p_id=0):
    if request.method not in ['GET', 'HEAD']:
        return json_error('Method not allowed', 405)
    try:
        p_id = int(p_id)
        if p_id < 1:
            raise ValueError
    except (ValueError, TypeError):
        return json_error('Bad request', 400)
    try:
        if request.path.startswith('/api/authors'):
            _person = Author.objects.get(id=p_id)
        else:
            _person = Artist.objects.get(id=p_id)
    except ObjectDoesNotExist:
        return json_error('Not found', 404)
    return _person_response(request, _person)


@csrf_exempt
def invalid_endpoint(request):
    return json_error('Invalid API endpoint', 501)


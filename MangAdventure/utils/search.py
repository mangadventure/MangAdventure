from django.db.models.query import Q
from reader.models import (
    Series, SeriesAlias, AuthorAlias, ArtistAlias
)


def parse(request):
    categories = request.GET.get('categories', '').split(',')
    return {
        'query': request.GET.get('q', ''),
        'author': request.GET.get('author', ''),
        'status': request.GET.get('status', 'any'),
        'categories': {
            'include': [c.lower() for c in categories
                        if len(c) and c[0] != '-'],
            'exclude': [c[1:].lower() for c in categories
                        if len(c) and c[0] == '-'],
        }
    }


def filter(params):
    filters = Q()
    if params['query']:
        filters = Q(title__icontains=params['query'])
        aliases = SeriesAlias.objects.filter(
            alias__icontains=params['query'])
        if len(aliases):
            filters |= Q(aliases__in=aliases)
    if params['author']:
        q = (Q(authors__name__icontains=params['author']) |
             Q(artists__name__icontains=params['author']))
        authors = AuthorAlias.objects.filter(
            alias__icontains=params['author'])
        if len(authors):
            q |= Q(authors__pk__in=authors)
        artists = ArtistAlias.objects.filter(
            alias__icontains=params['author'])
        if len(artists):
            q |= Q(artists__pk__in=artists)
        filters &= q
    if params['status'] != 'any':
        filters &= Q(completed=(params['status'] == 'completed'))
    categories = params['categories']
    if categories['include']:
        filters &= Q(categories__in=categories['include'])
    return filters, params['categories']['exclude']


def query(params, prefetch=True):
    filters, exclude = filter(params)
    if prefetch:
        related = ('chapters', 'authors', 'artists', 'categories')
        result = Series.objects.prefetch_related(*related).filter(
            filters).distinct().exclude(categories__in=exclude)
    else:
        result = Series.objects.filter(
            filters).distinct().exclude(categories__in=exclude)
    return result


def get_response(request, pre=True): return query(parse(request), pre)


__all__ = ['parse', 'filter', 'query', 'get_response']


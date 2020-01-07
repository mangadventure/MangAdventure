"""Functions used for searching."""

from typing import TYPE_CHECKING, List, NamedTuple, Tuple

from django.db.models.query import Q

from reader.models import ArtistAlias, AuthorAlias, Series, SeriesAlias

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models.query import QuerySet
    from django.http import HttpRequest


class _SearchParams(NamedTuple):
    """
    A class that represents search parameters.

    :cvar query: The value of the ``query`` parameter.
    :cvar author: The value of the ``author`` parameter.
    :cvar status: The value of the ``status`` parameter.
    :cvar categories: The values of the ``categories`` parameter
                      as a tuple of included/excluded categories.
    """
    query: str
    author: str
    status: str
    categories: Tuple[List[str], List[str]]


def parse(request: 'HttpRequest') -> _SearchParams:
    """
    Parse a request and return a :obj:`~collections.namedtuple`
    of search parameters.

    :param request: The original request.

    :return: The parameters of the request.
    """
    categories = request.GET.get('categories', '').split(',')
    return _SearchParams(
        query=request.GET.get('q', ''),
        author=request.GET.get('author', ''),
        status=request.GET.get('status', 'any'),
        categories=(
            [c.lower() for c in categories if len(c) and c[0] != '-'],
            [c[1:].lower() for c in categories if len(c) and c[0] == '-']
        )
    )


def qsfilter(params: _SearchParams) -> Tuple[Q, List[str]]:
    """
    Create a `queryset filter`_ from the given search parameters.

    :param params: A :obj:`~collection.namedtuple` of parameters.

    :return: A tuple containing the filter and the excluded categories.

    .. _`queryset filter`:
        https://docs.djangoproject.com/en/3.0/
        topics/db/queries/#complex-lookups-with-q
    """
    filters = Q()
    if params.query:
        filters = Q(title__icontains=params.query)
        aliases = SeriesAlias.objects.filter(
            alias__icontains=params.query
        )
        if len(aliases):
            filters |= Q(aliases__in=aliases)
    if params.author:
        q = Q(authors__name__icontains=params.author) | \
            Q(artists__name__icontains=params.author)
        authors = AuthorAlias.objects.filter(
            alias__icontains=params.author
        )
        if len(authors):
            q |= Q(authors__pk__in=authors)
        artists = ArtistAlias.objects.filter(
            alias__icontains=params.author
        )
        if len(artists):
            q |= Q(artists__pk__in=artists)
        filters &= q
    if params.status != 'any':
        filters &= Q(completed=(params.status == 'completed'))
    categories = params.categories
    if params.categories[0]:
        filters &= Q(categories__in=categories[0])
    return filters, categories[1]


def query(params: _SearchParams) -> 'QuerySet':
    """
    Get a queryset of :class:`Series` from the given search parameters.

    :param params: A :obj:`~collection.namedtuple` of parameters.

    :return: A queryset of series matching the given parameters.
    """
    filters, exclude = qsfilter(params)
    return Series.objects.filter(filters) \
        .distinct().exclude(categories__in=exclude)


def get_response(request: 'HttpRequest') -> 'QuerySet':
    """
    Get a queryset of :class:`Series` from the given request.

    :param request: The original request.

    :return: A queryset of series matching the parameters of the request.
    """
    slug = request.GET.get('slug')
    if slug:
        return Series.objects.filter(slug=slug)
    return query(parse(request))


__all__ = ['parse', 'qsfilter', 'query', 'get_response']

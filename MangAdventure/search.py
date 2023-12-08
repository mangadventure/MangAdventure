"""Functions used for searching."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, NamedTuple, Tuple

from django.db.models import Count, Max, Q, Sum
from django.utils import timezone as tz

from reader.models import Series

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

    def __bool__(self) -> bool:
        """
        Check whether the parameters can be used in a filter.

        :return: ``True`` if any parameter has a usable value.
        """
        return bool(
            self.query != '' or
            self.author != '' or
            self.status != '' or
            self.categories != ([], [])
        )


def parse(request: HttpRequest) -> _SearchParams:
    """
    Parse a request and return a :obj:`~collections.namedtuple`
    of search parameters.

    :param request: The original request.

    :return: The parameters of the request.
    """
    categories = request.GET.get('categories', '').split(',')
    return _SearchParams(
        query=request.GET.get('q', '').strip(),
        author=request.GET.get('author', '').strip(),
        status=request.GET.get('status', '').lower().strip(),
        categories=(
            [c.lower() for c in categories if c and c[0] != '-'],
            [c[1:].lower() for c in categories if c and c[0] == '-']
        )
    )


def qsfilter(params: _SearchParams) -> Q:
    """
    Create a `queryset filter`_ from the given search parameters.

    :param params: A :obj:`~collections.namedtuple` of parameters.

    :return: The created queryset filter.

    .. _`queryset filter`:
        https://docs.djangoproject.com/en/4.1/
        topics/db/queries/#complex-lookups-with-q
    """
    filters = Q()
    if params.query:
        filters = (
            Q(title__icontains=params.query) |
            Q(aliases__name__icontains=params.query)
        )
    if params.author:
        filters &= (
            Q(authors__name__icontains=params.author) |
            Q(artists__name__icontains=params.author) |
            Q(authors__aliases__name__icontains=params.author) |
            Q(artists__aliases__name__icontains=params.author)
        )
    if params.status and params.status != 'any':
        filters &= Q(status=params.status)
    included, excluded = params.categories
    if excluded:
        filters &= ~Q(categories__in=excluded)
    if included:
        filters &= Q(categories__in=included)
    return filters


def query(params: _SearchParams) -> QuerySet:
    """
    Get a queryset of :class:`~reader.models.Series`
    from the given search parameters.

    :param params: A :obj:`~collections.namedtuple` of parameters.

    :return: A queryset of series matching the given parameters.
    """
    if not params:
        return Series.objects.none()
    q = Q(chapters__published__lte=tz.now())
    return Series.objects.annotate(  # type: ignore
        chapter_count=Count('chapters', filter=q),
        latest_upload=Max('chapters__published', filter=q),
        views=Sum('chapters__views', distinct=True)
    ).complex_filter(
        qsfilter(params) & Q(chapter_count__gt=0)
    ).defer(
        'licensed', 'manager', 'created', 'modified'
    ).distinct()


def get_response(request: HttpRequest) -> QuerySet:
    """
    Get a queryset of :class:`~reader.models.Series` from the given request.

    :param request: The original request.

    :return: A queryset of series matching the parameters of the request.
    """
    if slug := request.GET.get('slug'):
        return Series.objects.filter(slug=slug)
    if params := parse(request):
        return query(params)
    return Series.objects.all()


__all__ = ['parse', 'qsfilter', 'query', 'get_response']

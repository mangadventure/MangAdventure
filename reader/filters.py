"""Custom filter backends for the API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from django.db.models import F

from rest_framework.exceptions import ValidationError
from rest_framework.filters import (
    BaseFilterBackend, OrderingFilter, SearchFilter
)

from reader.models import Chapter

if TYPE_CHECKING:  # pragma no cover
    from django.db.models.query import QuerySet  # isort:skip
    from rest_framework.request import Request  # isort:skip
    from rest_framework.viewsets import ViewSet  # isort:skip


class TitleFilter(SearchFilter):
    """Series title filter."""
    search_param = 'title'
    search_title = 'Title'
    search_description = 'Search by title.'

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        return super().filter_queryset(request, queryset, view)

    def get_search_fields(self, view: ViewSet,
                          request: Request) -> List[str]:
        return ['title', 'aliases__name']

    def get_search_terms(self, request: Request) -> List[str]:
        param = request.query_params.get(self.search_param, None)
        return [] if param is None else [param.replace('\x00', '')]


class AuthorFilter(SearchFilter):
    """Series author filter."""
    search_param = 'author'
    search_title = 'Author'
    search_description = 'Search by author name.'

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        return super().filter_queryset(request, queryset, view)

    def get_search_fields(self, view: ViewSet,
                          request: Request) -> List[str]:
        return ['authors__name', 'authors__aliases__name']

    def get_search_terms(self, request: Request) -> List[str]:
        param = request.query_params.get(self.search_param, None)
        return [] if param is None else [param.replace('\x00', '')]


class ArtistFilter(SearchFilter):
    """Series artist filter."""
    search_param = 'artist'
    search_title = 'Artist'
    search_description = 'Search by artist name.'

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        return super().filter_queryset(request, queryset, view)

    def get_search_fields(self, view: ViewSet,
                          request: Request) -> List[str]:
        return ['artists__name', 'artists__aliases__name']

    def get_search_terms(self, request: Request) -> List[str]:
        param = request.query_params.get(self.search_param, None)
        return [] if param is None else [param.replace('\x00', '')]


class StatusFilter(BaseFilterBackend):
    """Series status filter."""
    description = 'Filter by the status.'

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        return {
            'any': queryset,
            'completed': queryset.filter(completed=True),
            'ongoing': queryset.filter(completed=False)
        }.get(request.query_params.get('status', 'any').lower())

    def get_schema_operation_parameters(self, view: ViewSet) -> List[Dict]:
        return [{
            'name': 'status',
            'required': False,
            'in': 'query',
            'description': self.description,
            'schema': {
                'type': 'string',
                'default': 'any',
                'enum': ('any', 'completed', 'ongoing')
            }
        }]


class CategoriesFilter(BaseFilterBackend):
    """Series categories filter."""
    description = "Filter by categories. (prefix with '-' to exclude)"

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        categories = request.query_params.get('categories', '').split(',')
        include = [c.lower() for c in categories if c and c[0] != '-']
        exclude = [c[1:].lower() for c in categories if c and c[0] == '-']
        if include:
            queryset = queryset.filter(
                categories__in=list(map(str.lower, include))
            )
        if exclude:
            queryset = queryset.exclude(
                categories__in=list(map(str.lower, exclude))
            )
        return queryset

    def get_schema_operation_parameters(self, view: ViewSet) -> List[Dict]:
        return [{
            'name': 'categories',
            'required': False,
            'in': 'query',
            'description': self.description,
            'schema': {
                'type': 'array',
                'items': {'type': 'string'}
            },
            'style': 'form',
            'explode': False
        }]


class SlugFilter(SearchFilter):
    """Series slug filter."""
    search_param = 'slug'
    search_title = 'Slug'
    search_description = 'Filter by the slug.'

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        return super().filter_queryset(request, queryset, view)

    def get_search_fields(self, view: ViewSet,
                          request: Request) -> List[str]:
        return ['=slug']

    def get_search_terms(self, request: Request) -> List[str]:
        param = request.query_params.get(self.search_param, None)
        return [] if param is None else [param.replace('\x00', '')]


class SeriesSort(OrderingFilter):
    """Series sort order filter."""
    ordering_fields = ['title', 'latest_upload', 'chapter_count', 'views']
    ordering_description = "Change the sort order. ('-' means descending)"

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        return super().filter_queryset(request, queryset, view)

    def get_schema_operation_parameters(self, view: ViewSet) -> List[Dict]:
        params = super().get_schema_operation_parameters(view)
        params[0]['schema'].update({
            'default': 'title',
            'enum': self.ordering_fields + list(
                map('-'.__add__, self.ordering_fields)
            )
        })
        return params

    def to_html(self, *args, **kwargs) -> str:
        return ''  # remove from the template


class DateFormat(BaseFilterBackend):
    """Date format filter."""
    description = 'Change the displayed date format.'

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        return queryset  # no actual filtering is performed

    def get_schema_operation_parameters(self, view: ViewSet) -> List[Dict]:
        return [{
            'name': 'date_format',
            'required': False,
            'in': 'query',
            'description': self.description,
            'schema': {
                'type': 'string',
                'default': 'iso-8601',
                'enum': ('iso-8601', 'rfc-5322', 'timestamp')
            }
        }]


class ChapterFilter(SearchFilter):
    """Chapter series filter."""
    search_param = 'series'
    search_title = 'Series'
    search_description = "Filter by the series slug."

    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        if 'series' not in request.query_params.keys():
            raise ValidationError(detail={
                'error': "'series' is a required parameter."
            })
        queryset = queryset.filter(series__licensed=False)
        return super().filter_queryset(request, queryset, view)

    def get_search_fields(self, view: ViewSet,
                          request: Request) -> List[str]:
        return ['=series__slug']

    def get_search_terms(self, request: Request) -> List[str]:
        param = request.query_params.get(self.search_param, None)
        return [] if param is None else [param.replace('\x00', '')]

    def get_schema_operation_parameters(self, view: ViewSet) -> List[Dict]:
        return [{
            'name': self.search_param,
            'required': True,
            'in': 'query',
            'description': self.search_description,
            'schema': {
                'type': 'string',
                'pattern': '^[-a-zA-Z0-9_]+$'
            }
        }]


class PageFilter(BaseFilterBackend):
    """Chapter pages filter."""
    def filter_queryset(self, request: Request, queryset: QuerySet,
                        view: ViewSet) -> QuerySet:
        if view.action != 'list':
            return queryset
        params = {'series', 'volume', 'number'}
        if not params.issubset(request.query_params.keys()):
            raise ValidationError(detail={
                'error': f'{params} are required parameters.'
            })
        series = request.query_params['series']
        volume = request.query_params['volume']
        number = request.query_params['number']
        if request.query_params.get('track') == 'true':
            Chapter.objects.filter(
                series__slug=series, volume=volume, number=number
            ).update(views=F('views') + 1)
        return queryset.filter(
            chapter__series__slug=series,
            chapter__volume=volume, chapter__number=number
        ).order_by('number')

    def get_schema_operation_parameters(self, view: ViewSet) -> List[Dict]:
        return [{
            'name': 'series',
            'required': True,
            'in': 'query',
            'description': "The chapter's series slug.",
            'schema': {
                'type': 'string',
                'pattern': '^[-a-zA-Z0-9_]+$'
            },
        }, {
            'name': 'volume',
            'required': True,
            'in': 'query',
            'description': 'The volume of the chapter.',
            'schema': {
                'type': 'integer',
                'minimum': 0
            }
        }, {
            'name': 'number',
            'required': True,
            'in': 'query',
            'description': 'The number of the chapter.',
            'schema': {
                'type': 'integer',
                'minimum': 0
            }
        }, {
            'name': 'track',
            'required': False,
            'in': 'query',
            'description': 'Track chapter views.',
            'schema': {'type': 'boolean'}
        }]


#: The filters used in the series endpoint.
SERIES_FILTERS = (
    TitleFilter, AuthorFilter, ArtistFilter,
    StatusFilter, CategoriesFilter, SlugFilter, SeriesSort
)

#: The filters used in the chapters endpoint.
CHAPTER_FILTERS = (ChapterFilter, DateFormat)

#: The filters used in the pages endpoint.
PAGE_FILTERS = (PageFilter,)


__all__ = ['SERIES_FILTERS', 'CHAPTER_FILTERS', 'PAGE_FILTERS']

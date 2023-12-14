"""Pagination utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.pagination import BasePagination, PageNumberPagination
from rest_framework.response import Response

if TYPE_CHECKING:  # pragma: no cover
    from rest_framework.viewsets import ViewSet


class DummyPagination(BasePagination):
    """Dummy pagination class that simply wraps results."""

    def to_html(self) -> str:
        return ''

    def paginate_queryset(self, *args, **kwargs) -> list:
        return list(args[0])

    def get_paginated_response(self, data: Any) -> Response:
        return Response({'results': data})

    def get_paginated_response_schema(self, schema: dict) -> dict:
        return {'type': 'object', 'properties': {'results': schema}}


class PageLimitPagination(PageNumberPagination):
    """Pagination class that allows the user to limit the page size."""
    page_size_query_param = 'limit'

    def get_paginated_response(self, data: Any) -> Response:
        return Response({
            'total': self.page.paginator.count,  # type: ignore
            'last': not self.page.has_next(),  # type: ignore
            'results': data
        })

    def get_paginated_response_schema(self, schema: dict) -> dict:
        return {
            'type': 'object',
            'properties': {
                'total': {
                    'type': 'integer',
                    'example': self.page_size,
                    'description': 'The total number of results across pages.'
                },
                'last': {
                    'type': 'boolean',
                    'example': False,
                    'description': 'Denotes whether this is the last page.'
                },
                'results': schema
            }
        }

    def get_schema_operation_parameters(self, view: ViewSet) -> list[dict]:
        params = super().get_schema_operation_parameters(view)
        params[0]['schema']['minimum'] = 1
        params[1]['schema'] |= {
            'minimum': 1, 'default': self.page_size
        }
        return params


__all__ = ['DummyPagination', 'PageLimitPagination']

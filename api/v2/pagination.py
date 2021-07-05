"""Pagination utilities."""

from typing import Any, Dict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageLimitPagination(PageNumberPagination):
    """Pagination class that allows the user to limit the page size."""
    page_size = 100
    page_size_query_param = 'limit'

    def get_paginated_response(self, data: Any) -> Response:
        return Response({
            'count': self.page.paginator.count,
            'last': not self.page.has_next(),
            'results': data
        })

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 100,
                },
                'last': {
                    'type': 'boolean',
                    'example': False,
                },
                'results': schema,
            },
        }

    def get_schema_operation_parameters(self, view: Any) -> Dict:
        params = super().get_schema_operation_parameters(view)
        params[1]['schema']['default'] = self.page_size
        return params


__all__ = ['PageLimitPagination']

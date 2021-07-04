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
                    'default': 100,
                },
                'last': {
                    'type': 'boolean',
                    'example': False,
                },
                'results': schema,
            },
        }


__all__ = ['PageLimitPagination']

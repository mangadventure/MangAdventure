"""Content negotiation utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from rest_framework.negotiation import DefaultContentNegotiation

if TYPE_CHECKING:  # pragma: no cover
    from rest_framework.request import Request


class OpenAPIContentNegotiation(DefaultContentNegotiation):
    """Class that fixes content negotiation for the OpenAPI schema."""

    def get_accept_list(self, request: Request) -> List[str]:
        return super().get_accept_list(request) + [
            'application/vnd.oai.openapi+json'
        ]


__all__ = ['OpenAPIContentNegotiation']

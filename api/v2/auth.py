"""Authentication & authorization utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoObjectPermissions

from users.models import ApiKey

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import User  # isort:skip
    from rest_framework.request import Request  # isort:skip


class ApiKeyAuthentication(TokenAuthentication):
    """API key authentication class."""
    keyword = 'X-API-Key'
    model = ApiKey

    def authenticate(self, request: Request) -> tuple[User, ApiKey] | None:
        token = request.headers.get(
            self.keyword, request.GET.get('api_key')
        )
        return self.authenticate_credentials(token) if token else None


class ScanlatorPermissions(DjangoObjectPermissions):
    """Authorization class for scanlators."""
    authenticated_users_only = False


__all__ = ['ApiKeyAuthentication', 'ScanlatorPermissions']

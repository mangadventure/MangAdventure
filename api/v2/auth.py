"""Authentication & authorization utilities."""

from typing import TYPE_CHECKING, Optional, Tuple

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoObjectPermissions

from users.models import ApiKey

if TYPE_CHECKING:  # pragma: no cover
    from rest_framework.request import Request


class ApiKeyAuthentication(TokenAuthentication):
    """API key authentication class."""
    keyword = 'X-API-Key'
    model = ApiKey

    def authenticate(self, request: 'Request') -> Optional[Tuple]:
        token = request.headers.get(
            self.keyword, request.GET.get('api_key')
        )
        return self.authenticate_credentials(token) if token else None


class ScanlatorPermissions(DjangoObjectPermissions):
    """Authorization class for scanlators."""
    authenticated_users_only = False


__all__ = ['ApiKeyAuthentication', 'ScanlatorPermissions']

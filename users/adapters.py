"""Custom adapters for :auth:`django-allauth <advanced.html>`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_next_redirect_url
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest  # isort:skip
    from allauth.socialaccount.models import SocialAccount  # isort:skip


class AccountAdapter(DefaultAccountAdapter):
    """Adapter for user accounts."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """
        Return the URL to redirect to after a successful login.

        :param request: The original request.

        :return: The URL of the redirect.
        """
        return get_next_redirect_url(request) or '/user'

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        """
        Return the URL to redirect to after a successful logout.

        :param request: The original request.

        :return: The URL of the redirect.
        """
        return get_next_redirect_url(request) or '/'


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter for OAuth accounts."""

    def get_connect_redirect_url(self, request: HttpRequest,
                                 social_account: SocialAccount) -> str:
        """
        Return the URL to redirect to after a successful connection.

        :param request: The original request.
        :param social_account: The connected OAuth account.

        :return: The URL of the redirect.
        """
        return get_next_redirect_url(request) or '/user'


__all__ = ['AccountAdapter', 'SocialAccountAdapter']

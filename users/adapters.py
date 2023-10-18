"""Custom adapters for :auth:`django-allauth <advanced.html>`."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest  # isort:skip
    from allauth.socialaccount.models import SocialAccount  # isort:skip


_is_safe_url = partial(
    url_has_allowed_host_and_scheme,
    allowed_hosts=settings.ALLOWED_HOSTS,
    require_https=settings.SECURE_SSL_REDIRECT
)


class AccountAdapter(DefaultAccountAdapter):
    """Adapter for user accounts."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """
        Return the URL to redirect to after a successful login.

        :param request: The original request.

        :return: The URL of the redirect.
        """
        url = request.GET.get('next')
        return url if url and _is_safe_url(url) else '/user'

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        """
        Return the URL to redirect to after a successful logout.

        :param request: The original request.

        :return: The URL of the redirect.
        """
        url = request.POST.get('next')
        return url if url and _is_safe_url(url) else '/'


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
        url = request.POST.get('next') or request.GET.get('next')
        return url if url and _is_safe_url(url) else '/user'


__all__ = ['AccountAdapter', 'SocialAccountAdapter']

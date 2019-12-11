"""Custom adapters for :auth:`django-allauth <advanced.html>`."""

from typing import TYPE_CHECKING

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

if TYPE_CHECKING:
    from django.http import HttpRequest
    from allauth.socialaccount.models import SocialAccount


class AccountAdapter(DefaultAccountAdapter):
    """Adapter for user accounts."""
    def get_login_redirect_url(self, request: 'HttpRequest') -> str:
        """
        Return the URL to redirect to after a successful login.

        :param request: The original request.

        :return: The URL of the redirect.
        """
        return request.GET.get('next', '/user')

    def get_logout_redirect_url(self, request: 'HttpRequest') -> str:
        """
        Return the URL to redirect to after a successful logout.

        :param request: The original request.

        :return: The URL of the redirect.
        """
        return request.POST.get('next', '/')


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter for OAuth accounts."""
    def get_connect_redirect_url(self, request: 'HttpRequest',
                                 social_account: 'SocialAccount') -> str:
        """
        Return the URL to redirect to after a successful connection.

        :param request: The original request.
        :param social_account: The connected OAuth account.

        :return: The URL of the redirect.
        """
        return request.POST.get('next', '/user')


__all__ = ['AccountAdapter', 'SocialAccountAdapter']

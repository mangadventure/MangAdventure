"""Template tags of the users app."""

from typing import List

from django.template.defaultfilters import register

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers import registry
from allauth.socialaccount.templatetags.socialaccount import (
    provider_login_url as _provider_login_url
)


@register.simple_tag
def get_oauth_providers() -> List:
    """Get a list of available OAuth providers."""
    registry.load()
    return [
        registry.provider_map[p](None) for p in
        SocialApp.objects.values_list('provider', flat=True)
    ]


# :func:`allauth.socialaccount.templatetags.socialaccount.provider_login_url`
provider_login_url = register.tag(_provider_login_url)

__all__ = ['get_oauth_providers', 'provider_login_url']

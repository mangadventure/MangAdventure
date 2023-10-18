"""Template tags of the users app."""

from typing import Dict, List

from django.core.cache import cache
from django.template.defaultfilters import register

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.templatetags.socialaccount import (
    provider_login_url as _provider_login_url
)


@register.simple_tag
def get_oauth_providers() -> List[Dict[str, str]]:
    """Get a list of available OAuth providers."""
    if not (providers := cache.get('oauth.providers')):
        providers = list(SocialApp.objects.values('provider', 'name'))
        cache.add('oauth.providers', providers)
    return providers


# :func:`allauth.socialaccount.templatetags.socialaccount.provider_login_url`
provider_login_url = register.simple_tag(
    _provider_login_url, takes_context=True
)

__all__ = ['get_oauth_providers', 'provider_login_url']

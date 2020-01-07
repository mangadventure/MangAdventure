"""Template tags of the users app."""

from operator import attrgetter
from typing import Iterable, List

from django.template.defaultfilters import register

from allauth.socialaccount.models import SocialApp


@register.filter
def available(providers: Iterable[SocialApp]) -> List[SocialApp]:
    """
    Filter out the unavailable OAuth providers.

    :param providers: The original list of OAuth providers.

    :return: A list of available OAuth providers.
    """
    ids = list(map(attrgetter('id'), providers))
    objects = SocialApp.objects \
        .filter(provider__in=ids).values_list('provider', flat=True)
    return list(filter(lambda p: p.id in objects, providers))


__all__ = ['available']

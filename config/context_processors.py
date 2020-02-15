"""Custom context processors."""

from typing import TYPE_CHECKING, Dict

from django.conf import settings

from MangAdventure import __version__ as VERSION
from MangAdventure.jsonld import schema

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


def extra_settings(request: 'HttpRequest') -> Dict:
    """
    Context processor which defines some settings variables.

    * ``MANGADV_VERSION``: The current version of MangAdventure.
    * ``PAGE_URL``: The complete absolute URI of the request.
    * ``CANON_URL``: The absolute URI of the request minus the query string.
    * ``config``: A reference to :const:`MangAdventure.settings.CONFIG`.

    :param request: The current HTTP request.

    :return: A dictionary containing the variables.
    """
    full_uri = request.build_absolute_uri()
    base_uri = request.build_absolute_uri('/')
    path_uri = request.build_absolute_uri(request.path)
    logo_uri = request.build_absolute_uri(settings.CONFIG['LOGO_OG'])
    searchbox = schema('WebSite', {
        'url': base_uri,
        'potentialAction': [{
            '@type': 'SearchAction',
            'target': f'{base_uri}search/?q={{query}}',
            'query-input': 'required name=query'
        }]
    })
    organization = schema('Organization', {
        'url': base_uri,
        'logo': logo_uri,
        'name': settings.CONFIG['NAME'],
        'description': settings.CONFIG['DESCRIPTION'],
        # 'email': settings.DEFAULT_FROM_EMAIL
    })
    return {
        'MANGADV_VERSION': VERSION,
        'PAGE_URL': full_uri,
        'CANON_URL': path_uri,
        'config': settings.CONFIG,
        'searchbox': searchbox,
        'organization': organization
    }


__all__ = ['extra_settings']

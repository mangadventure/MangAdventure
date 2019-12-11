"""Custom context processors."""

from typing import TYPE_CHECKING, Dict

from django.conf import settings

from MangAdventure import __version__ as VERSION

if TYPE_CHECKING:
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
    uri = request.build_absolute_uri()
    return {
        'MANGADV_VERSION': VERSION,
        'PAGE_URL': uri,
        'CANON_URL': uri.split('?')[0],
        'config': settings.CONFIG,
    }


__all__ = ['extra_settings']

from django.conf import settings

from MangAdventure import __version__ as VERSION


def extra_settings(request):
    uri = request.build_absolute_uri()
    return {
        'MANGADV_VERSION': VERSION,
        'PAGE_URL': uri,
        'CANON_URL': uri.split('?')[0],
        'config': settings.CONFIG,
    }

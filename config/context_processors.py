from MangAdventure import __version__ as version


def extra_settings(request):
    return {
        'MANGADV_VERSION': version,
        'PAGE_URL': request.build_absolute_uri(),
    }

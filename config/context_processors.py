from MangAdventure import __version__ as version
from django.apps import apps


def extra_settings(request):
    return {
        'MANGADV_VERSION': version,
        'PAGE_URL': request.build_absolute_uri(),
        'USERS_ENABLED': apps.is_installed('users')
    }


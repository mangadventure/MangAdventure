from django.contrib.sites.shortcuts import get_current_site
from MangAdventure import __version__ as version
from . import CONFIG


def extra_settings(request):
    try:
        site = CONFIG['site_url']
        if not site:
            raise KeyError
    except KeyError:
        site = 'http://' + get_current_site(request).domain
    return {
        'SITE_URL': site,
        'MANGADV_VERSION': version,
    }


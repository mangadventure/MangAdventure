from django.contrib.sites.shortcuts import get_current_site
from MangAdventure import __version__ as version
from os import environ as env
from . import CONFIG


def extra_settings(request):
    try:
        site = CONFIG['site_url']
        if not site:
            raise KeyError
    except KeyError:
        if env.get('HTTPS', '') == 'on':
            protocol = 'https://'
        else:
            protocol = 'http://'
        site = protocol + get_current_site(request).domain
    return {
        'SITE_URL': site,
        'MANGADV_VERSION': version,
        'PAGE_URL': request.build_absolute_uri()
    }


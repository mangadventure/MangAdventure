from MangAdventure import __version__ as version
from . import CONFIG


def extra_settings(request):
    try:
        site = CONFIG['site_url']
        if not site:
            raise KeyError
    except KeyError:
        from django.contrib.sites.shortcuts import get_current_site
        from os import environ as env
        if env.get('HTTPS', '').lower() == 'on':
            protocol = 'https://'
        else:
            protocol = 'http://'
        site = protocol + get_current_site(request).domain
    return {
        'SITE_URL': site,
        'MANGADV_VERSION': version,
        'PAGE_URL': request.build_absolute_uri()
    }


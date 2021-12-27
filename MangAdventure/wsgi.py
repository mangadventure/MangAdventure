"""WSGI definitions."""

from os import environ as env

from django.core.wsgi import get_wsgi_application

env.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')

#: Django's WSGI application instance.
application = get_wsgi_application()

# HACK: run before the app starts or reloads
__import__('config').apps.SiteConfig._init()

__all__ = ['application']

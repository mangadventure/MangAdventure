"""WSGI definitions."""

from os import environ as env

from django.core.wsgi import get_wsgi_application

env.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')

#: Django's WSGI application instance.
application = get_wsgi_application()

__all__ = ['application']

"""
WSGI settings for MangAdventure project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
from os import environ as env
from dj_static import Cling, MediaCling

env.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')

application = Cling(MediaCling(get_wsgi_application()))


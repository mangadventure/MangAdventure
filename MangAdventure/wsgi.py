"""
WSGI settings for MangAdventure project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
from os import environ as env

env.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')

application = get_wsgi_application()


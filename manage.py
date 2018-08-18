#!/usr/bin/env python3

from os import environ as env
from sys import argv

if __name__ == '__main__':
    env.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as err:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available in your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from err
    execute_from_command_line(argv)

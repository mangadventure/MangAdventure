#!/usr/bin/env python

from os import environ as env
from sys import argv


def main():
    env.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available in your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    execute_from_command_line(argv)


if __name__ == '__main__':
    main()

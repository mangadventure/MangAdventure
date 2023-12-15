#!/usr/bin/env python3

from os import environ
from sys import argv


def run():
    environ['DJANGO_SETTINGS_MODULE'] = 'MangAdventure.settings'
    from django.core.management import execute_from_command_line
    execute_from_command_line(argv)


if __name__ == '__main__':
    run()

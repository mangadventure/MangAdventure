from django.utils.six import moves
from os import path

RawConfigParser = moves.configparser.RawConfigParser
NoSectionError = moves.configparser.NoSectionError

PARSER = RawConfigParser()
CONFIG_DIR = path.dirname(path.dirname(path.abspath(__file__)))
CONFIG_FILE = path.join(CONFIG_DIR, 'config.ini')


def write_config(section, key, value):
    PARSER.read(CONFIG_FILE)
    if not PARSER.has_section(section):
        PARSER.add_section(section)
    if value.startswith('#'):
        value = "'{}'".format(value)
    PARSER.set(section, key, value)
    with open(CONFIG_FILE, 'w+') as config:
        PARSER.write(config)
    if hasattr(PARSER, 'clear'):
        PARSER.clear()


def read_config(section=None):
    PARSER.read(CONFIG_FILE)
    if section is not None:
        try:
            config = dict(PARSER.items(section))
        except NoSectionError:
            config = dict()
    else:
        config = dict((s, dict(PARSER.items(s)))
                      for s in PARSER.sections())
    if hasattr(PARSER, 'clear'):
        PARSER.clear()
    return config


CONFIG = read_config('settings')

__all__ = ['write_config', 'read_config', 'CONFIG']


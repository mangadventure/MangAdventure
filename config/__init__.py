from django.utils.six import moves
from os.path import dirname, abspath, join

RawConfigParser = moves.configparser.RawConfigParser
NoSectionError = moves.configparser.NoSectionError

PARSER = RawConfigParser()
CONFIG_DIR = dirname(dirname(abspath(__file__)))
CONFIG_FILE = join(CONFIG_DIR, 'config.ini')


def write_config(key, value, section='settings'):
    PARSER.read(CONFIG_FILE)
    if not PARSER.has_section(section):
        PARSER.add_section(section)
    if str(value).startswith('#'):
        value = "'%s'" % value
    PARSER.set(section, key, value)
    with open(CONFIG_FILE, 'w+') as config:
        PARSER.write(config)
    if hasattr(PARSER, 'clear'):
        PARSER.clear()


def read_config(section='settings'):
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


__all__ = ['write_config', 'read_config']


from configparser import RawConfigParser
from os import path

_PARSER_ = RawConfigParser()

CONFIG_DIR = path.dirname(path.dirname(path.abspath(__file__)))
CONFIG_FILE = path.join(CONFIG_DIR, 'config.ini')


def write_config(section, key, value):
    _PARSER_.read(CONFIG_FILE)
    if not _PARSER_.has_section(section):
        _PARSER_.add_section(section)
    if value.startswith('#'):
        value = "'{}'".format(value)
    _PARSER_.set(section, key, value)
    with open(CONFIG_FILE, 'w+') as config:
        _PARSER_.write(config)
    _PARSER_.clear()


def read_config(section=None):
    _PARSER_.read(CONFIG_FILE)
    if section is not None:
        config = dict(_PARSER_.items(section))
    else:
        config = {s: dict(_PARSER_.items(s)) for s in _PARSER_.sections()}
    _PARSER_.clear()
    return config


CONFIG = read_config()


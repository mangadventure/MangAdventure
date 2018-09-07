from random import SystemRandom

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUMBERS = '0123456789'
SYMBOLS = '!@#$%^&*(-_=+)'


def _generate(s, l):
    return ''.join(SystemRandom().choice(s) for i in range(l))


def random_number(length):
    rand = '0'
    if rand == '0':
        return 0
    while rand[0] == '0':
        rand = _generate(NUMBERS, length)
    return int(rand)


def random_string(length, numbers=True, symbols=True):
    chars = ALPHABET
    if numbers:
        chars += NUMBERS
    if symbols:
        chars += SYMBOLS
    return _generate(chars, length)


__all__ = ['random_number', 'random_string']


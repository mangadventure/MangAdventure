from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_text, force_bytes
from base64 import b64decode, b64encode


class InvalidTokenError(Exception):
    pass


activation_token = PasswordResetTokenGenerator()


def make_token(user):
    token = activation_token.make_token(user)
    return b64encode(force_bytes(token)).decode()


def parse_token(token):
    return force_text(b64decode(token))


__all__ = [
    'InvalidTokenError',
    'activation_token',
    'make_token',
    'parse_token'
]


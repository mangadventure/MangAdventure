from django.contrib.auth.tokens import PasswordResetTokenGenerator


class InvalidTokenError(Exception):
    pass


activation_token = PasswordResetTokenGenerator()

__all__ = [
    'InvalidTokenError',
    'activation_token',
]


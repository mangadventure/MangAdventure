"""Signal receivers for the users app."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.dispatch import receiver

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


@receiver(email_confirmed)
def update_user_email(sender: Type[EmailAddress], request: HttpRequest,
                      email_address: EmailAddress, **kwargs):
    """
    Receive a signal when an email address is updated and confirmed.

    When the signal is received, the new ``email_address``
    is made primary and the old email addresses are deleted.

    :param sender: The model class that sent the signal.
    :param request: The original request.
    :param email_address: The new email address.
    """
    email_address.user.is_active = True
    # Make new email_address primary
    email_address.set_as_primary()
    # Get rid of old email addresses
    EmailAddress.objects.filter(
        user=email_address.user, primary=False
    ).delete()


__all__ = ['update_user_email']

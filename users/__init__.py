"""The app that handles users."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import User


def get_user_display(user: User) -> str:
    """
    Display the name of the user.

    :param user: A ``User`` model instance.

    :return: The user's full name if available, otherwise the username.
    """
    full_name = user.get_full_name()
    return full_name if len(full_name.strip()) else user.username


__all__ = ['get_user_display']

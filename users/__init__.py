"""The app that handles users."""


# XXX: Can't add type hint due to circular import.
def get_user_display(user) -> str:
    """
    Display the name of the user.

    :param user: A ``User`` model instance.
    :type user: :class:`~django.contrib.auth.models.User`

    :return: The user's full name if available, otherwise the username.
    """
    full_name = user.get_full_name()
    return full_name if len(full_name.strip()) else user.username


__all__ = ['get_user_display']

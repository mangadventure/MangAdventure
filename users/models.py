"""Database models for the users app."""

from hashlib import blake2b
from pathlib import PurePath
from secrets import token_hex

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from MangAdventure import storage, validators

from reader.models import Series


def _avatar_uploader(obj: 'UserProfile', name: str) -> str:
    name = f'avatar.{name.split(".")[-1]}'
    return str(obj.get_directory() / name)


class Bookmark(models.Model):
    """A model representing a bookmark."""
    #: The series this bookmark belongs to.
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    #: The user this bookmark belongs to.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks'
    )

    class Meta:
        unique_together = ('series', 'user')


class UserProfile(models.Model):
    """
    A model representing a user's profile.

    .. admonition:: TODO
       :class: warning

       Add links and let users hide their e-mail.
    """
    #: The user this profile belongs to.
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    #: The bio of the user.
    bio = models.TextField(
        blank=True, verbose_name='biography',
        help_text="The user's biography."
    )
    #: The avatar of the user.
    avatar = models.ImageField(
        help_text="The user's avatar image. Must be up to 2 MBs.",
        validators=(validators.FileSizeValidator(2),),
        storage=storage.CDNStorage((150, 150)),
        upload_to=_avatar_uploader, blank=True
    )
    #: The token of the user. Used in the bookmarks feed.
    token = models.CharField(
        auto_created=True, max_length=32, unique=True, editable=False
    )

    def save(self, *args, **kwargs):
        """Save the current instance."""
        if not self.token:
            data = f'{self.user.username}:{self.user.password}'
            self.token = blake2b(
                data.encode(), digest_size=16,
                key=settings.SECRET_KEY.encode()
            ).hexdigest()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL of the object.

        :return: The URL of :func:`users.views.profile`.
        """
        return f'{reverse("user_profile")}?id={self.id}'

    def get_directory(self) -> PurePath:
        """
        Get the storage directory of the object.

        :return: A path relative to
                 :const:`~MangAdventure.settings.MEDIA_ROOT`.
        """
        return PurePath('users', str(self.id))

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The user as a string.
        """
        return str(self.user)

    def __hash__(self) -> int:
        """
        Return the hash of the object.

        :return: An integer hash value.
        """
        return int(self.token, 16) & 0x7FFFFFFF


class ApiKey(models.Model):
    """A model that contains a user's API key."""
    #: The API key of the user.
    key = models.CharField(
        max_length=64, primary_key=True, default=token_hex
    )
    #: The user this key belongs to.
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, related_name='api_key'
    )
    #: The creation date of the key.
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The key as a string.
        """
        return str(self.key)

    def __hash__(self) -> int:
        """
        Return the hash of the object.

        :return: An integer hash value.
        """
        return int(self.key, 16) & 0x7FFFFFFF


__all__ = ['Bookmark', 'UserProfile', 'ApiKey']

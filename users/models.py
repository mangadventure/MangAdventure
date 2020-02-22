"""Database models for the users app."""

from pathlib import PurePath

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from MangAdventure import storage, validators

from reader.models import Series

try:  # pragma: no cover
    from hmac import digest
except ImportError:  # pragma: no cover
    # XXX: hmac.digest is not available in 3.6
    from hmac import HMAC, new as digest
    HMAC.hex = HMAC.hexdigest


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
        data = f'{self.user.username}:{self.user.password}'
        self.token = digest(
            settings.SECRET_KEY.encode(),
            data.encode(), 'shake128'
        ).hex()
        super(UserProfile, self).save(*args, **kwargs)

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
        return abs(int(self.token, 16))


__all__ = ['Bookmark', 'UserProfile']

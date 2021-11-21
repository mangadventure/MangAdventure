"""Custom validators."""

from __future__ import annotations

from io import BytesIO
from os import remove
from typing import Any
from zipfile import BadZipfile, ZipFile

from django.core.exceptions import ValidationError
# XXX: not parsed properly when under TYPE_CHECKING
from django.core.files import File
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

from PIL import Image


def _remove_file(file: File):
    try:
        remove(file.path)
    except FileNotFoundError:
        pass


@deconstructible
class FileSizeValidator:
    """
    Validates that a file's size is not greater than ``max_mb``.

    :param max_mb: The maximum size of the file in megabytes.
    """
    #: The error message of the validator.
    message = 'File too large. Maximum file size allowed is %(max)d MBs.'
    #: The error code of the validator.
    code = 'file_too_large'

    def __init__(self, max_mb: int = 10):
        self.max_mb = max_mb

    def __call__(self, file: File):
        """
        Call the validator on the given file.

        :param file: The file to be validated.

        :raises ValidationError: If the file is too large.
        """
        if file.size >= self.max_mb << 20:
            if hasattr(file, 'path'):
                _remove_file(file)
            raise ValidationError(
                self.message, code=self.code,
                params={'max': self.max_mb}
            )

    def __eq__(self, other: Any) -> bool:  # pragma: no cover
        """
        Check if this object is equal to another.

        :param other: Any other object.

        :return: ``True`` if the objects are equal.
        """
        return (
            isinstance(other, FileSizeValidator) and
            self.max_mb == other.max_mb
        )

    def __hash__(self) -> int:  # pragma: no cover
        """
        Return the hash of the object.

        :return: An integer hash value.
        """
        return hash(self.code) | self.max_mb


def zipfile_validator(file: File):
    """
    Validate a zip file:

    * It must be a valid :class:`~zipfile.ZipFile`.
    * It must only contain image files.
    * It cannot contain more than 1 subfolder.

    :param file: The file to be validated.

    :raises ValidationError: If any of the validations failed.
    """
    messages = (
        'The file cannot contain more than 1 subfolder.',
        'The file must only contain image files.',
        'The file must be in zip/cbz format.'
    )
    codes = ('no_multiple_subfolders', 'only_images', 'invalid_format')
    zf = None
    try:
        zf = ZipFile(file)
    except BadZipfile as err:
        _remove_file(file)
        raise ValidationError(messages[2], code=codes[2]) from err
    else:
        first_folder = True
        for f in zf.namelist():
            if zf.getinfo(f).is_dir():
                if first_folder:
                    first_folder = False
                    continue
                _remove_file(file)
                raise ValidationError(messages[0], code=codes[0])
            try:
                data = BytesIO(zf.read(f))
                Image.open(data).verify()
            except Exception as exc:
                _remove_file(file)
                raise ValidationError(messages[1], code=codes[1]) from exc
    finally:
        if zf:
            zf.close()


class DiscordServerValidator(RegexValidator):
    """Validates a Discord server URL."""
    regex = r'^https://discord\.(gg|me)/[A-Za-z0-9_%-]+$'
    message = 'Invalid Discord server URL.'
    code = 'invalid_discord_url'


class TwitterNameValidator(RegexValidator):
    """Validates a Twitter name."""
    regex = r'^[A-Za-z0-9_-]{1,15}$'
    message = 'Invalid Twitter username.'
    code = 'invalid_twitter_name'


class DiscordNameValidator(RegexValidator):
    """Validates a Discord name."""
    regex = r'^.{1,32}#[0-9]{4}$'
    message = 'Invalid Discord username and discriminator.'
    code = 'invalid_discord_name'


class RedditNameValidator(RegexValidator):
    """Validates a Reddit name."""
    regex = r'^(/[ur]/)?[A-Za-z0-9_]{3,21}$'
    message = 'Invalid Reddit username or subreddit name.'
    code = 'invalid_reddit_name'


__all__ = [
    'FileSizeValidator', 'DiscordServerValidator',
    'zipfile_validator', 'TwitterNameValidator',
    'DiscordNameValidator', 'RedditNameValidator'
]

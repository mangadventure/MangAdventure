"""Custom validators."""

from io import BytesIO
from os import remove
from typing import TYPE_CHECKING
from zipfile import BadZipfile, ZipFile

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator

from PIL import Image

if TYPE_CHECKING:  # pragma: no cover
    from django.core.files import File


def _remove_file(file: 'File'):
    try:
        remove(file.path)
    except FileNotFoundError:
        pass


class FileSizeValidator(BaseValidator):
    """
    Validates that a file's size is not greater than ``max_mb``.

    :param max_mb: The maximum size of the file in megabytes.
    """
    message = 'File too large. Maximum file size allowed is %(max)d MBs.'
    code = 'file_too_large'

    def __init__(self, max_mb: int = 10):
        self.max_mb = max_mb
        super(FileSizeValidator, self).__init__(max_mb)

    def __call__(self, file: 'File'):
        """
        Call the validator on the given file.

        :param file: The file to be validated.

        :raises ValidationError: If the file is too large.
        """
        if file.size >= self.max_mb << 20:
            _remove_file(file)
            raise ValidationError(
                self.message, code=self.code,
                params={'max': self.max_mb}
            )


def zipfile_validator(file: 'File'):
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


def discord_server_validator(url: str):
    """
    Call :class:`~django.core.validators.RegexValidator`
    to validate a Discord server URL.

    :param url: The Discord server URL to be validated.

    :raises ValidationError: If the URL is invalid.
    """
    RegexValidator(
        regex=r'^https://discord\.(gg|me)/[A-Za-z0-9_%-]+$',
        message='Invalid Discord server URL.',
        code='invalid_discord_url'
    ).__call__(url)


def twitter_name_validator(name: str):
    """
    Call :class:`~django.core.validators.RegexValidator`
    to validate a Twitter name.

    :param file: The Twitter name to be validated.

    :raises ValidationError: If the name is invalid.
    """
    RegexValidator(
        regex=r'^[A-Za-z0-9_-]{1,15}$',
        message='Invalid Twitter username.',
        code='invalid_twitter_name'
    ).__call__(name)


def discord_name_validator(name: str):
    """
    Call :class:`~django.core.validators.RegexValidator`
    to validate a Discord name.

    :param file: The Discord name to be validated.

    :raises ValidationError: If the name is invalid.
    """
    RegexValidator(
        regex=r'^.{1,32}#[0-9]{4}$',
        message='Invalid Discord username'
                ' and discriminator.',
        code='invalid_discord_name'
    ).__call__(name)


def reddit_name_validator(name: str):
    """
    Call :class:`~django.core.validators.RegexValidator`
    to validate a Reddit name.

    :param file: The Reddit name to be validated.

    :raises ValidationError: If the name is invalid.
    """
    RegexValidator(
        regex=r'^(/[ur]/)?[A-Za-z0-9_]{3,21}$',
        message='Invalid Reddit username or subreddit name.',
        code='invalid_reddit_name'
    ).__call__(name)


__all__ = [
    'FileSizeValidator', 'discord_server_validator',
    'zipfile_validator', 'twitter_name_validator',
    'discord_name_validator', 'reddit_name_validator'
]

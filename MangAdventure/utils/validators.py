from io import BytesIO
from os import remove
from zipfile import BadZipfile, ZipFile

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator

from PIL import Image

def _remove_file(file):
    try:
        remove(file.path)
    except FileNotFoundError:
        pass


class FileSizeValidator(BaseValidator):
    message = 'File too large. Maximum file size allowed is %(max)d MBs.'
    code = 'file_too_large'

    def __init__(self, max_mb=10):
        self.max_mb = max_mb
        super(FileSizeValidator, self).__init__(max_mb)

    def __call__(self, _file):
        if _file.size >= (self.max_mb * 1024 * 1024):
            _remove_file(_file)
            raise ValidationError(
                message=self.message, code=self.code,
                params={'max': self.max_mb}
            )


def zipfile_validator(_file):
    messages = (
        'The file cannot contain more than 1 subfolder.',
        'The file must only contain image files.',
        'The file must be in zip/cbz format.'
    )
    codes = ('no_multiple_subfolders', 'only_images', 'invalid_format')
    try:
        zip_file = ZipFile(_file)
    except BadZipfile:
        _remove_file(_file)
        raise ValidationError(message=messages[2], code=codes[2])
    first_folder = True
    for f in zip_file.namelist():
        if zip_file.getinfo(f).is_dir():
            if first_folder:
                first_folder = False
                continue
            _remove_file(_file)
            raise ValidationError(message=messages[0], code=codes[0])
        try:
            data = zip_file.read(f)
            img = Image.open(BytesIO(data))
            img.verify()
        except OSError:
            _remove_file(_file)
            raise ValidationError(message=messages[1], code=codes[1])


def discord_server_validator(url):
    return RegexValidator(
        regex=r'^https://discord\.(gg|me)/[A-Za-z0-9_%-]+$',
        message='Invalid Discord server URL.',
        code='invalid_discord_url'
    ).__call__(url)


def twitter_name_validator(name):
    return RegexValidator(
        regex=r'^[A-Za-z0-9_-]{1,15}$',
        message='Invalid Twitter username.',
        code='invalid_twitter_name'
    ).__call__(name)


def discord_name_validator(name):
    return RegexValidator(
        regex=r'^.{1,32}#[0-9]{4}$',
        message='Invalid Discord username'
                ' and discriminator.',
        code='invalid_discord_name'
    ).__call__(name)


def reddit_name_validator(name):
    return RegexValidator(
        regex=r'^(/[ur]/)?[A-Za-z0-9_]{3,21}$',
        message='Invalid Reddit username or subreddit name.',
        code='invalid_reddit_name'
    ).__call__(name)


__all__ = [
    'FileSizeValidator', 'discord_server_validator',
    'zipfile_validator', 'twitter_name_validator',
    'discord_name_validator', 'reddit_name_validator'
]

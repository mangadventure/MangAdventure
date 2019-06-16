from io import BytesIO
from os import remove
from re import compile as reg
from zipfile import ZipFile, error as BadZipfile

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator

from PIL import Image


def _is_dir(f): return f.filename[-1] == '/'


def _remove_file(_file):
    try:
        remove(_file.path)
    except OSError as err:
        # Ignore FileNotFoundError
        if err.errno != 2: raise err


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


class UsernameValidator(RegexValidator):
    def __init__(self, **kwargs):
        self.regex = reg(kwargs['regex'])
        self.message = kwargs['message'] or 'Invalid username.'
        self.code = kwargs['code'] or 'invalid_username'
        super(UsernameValidator, self).__init__(**kwargs)

    def __call__(self, username):
        if not self.regex.match(str(username)):
            raise ValidationError(message=self.message, code=self.code)


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
        if _is_dir(zip_file.getinfo(f)):
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
    regex = reg(r'^(https?://)?discord\.(gg|me)/[A-Za-z0-9_%-]+$')
    message = 'Invalid Discord server URL.'
    code = 'invalid_discord_url'
    if not regex.match(str(url)):
        raise ValidationError(message, code)


def twitter_name_validator(username):
    return UsernameValidator(
        regex=r'^[A-Za-z0-9_]{1,15}$',
        message='Invalid Twitter username.',
        code='invalid_twitter_name'
    ).__call__(username)


def discord_name_validator(username):
    return UsernameValidator(
        regex=r'^(.*){2,32}#[0-9]{4}$',
        message='Invalid Discord username'
                ' and discriminator.',
        code='invalid_discord_name'
    ).__call__(username)


def reddit_name_validator(reddit_name):
    return UsernameValidator(
        regex=r'^(/[ur]/)?[\w\d-]{3,21}$',
        message='Invalid Reddit username or subreddit name.',
        code='invalid_reddit_name'
    ).__call__(reddit_name)


__all__ = [
    'FileSizeValidator', 'UsernameValidator',
    'discord_server_validator', 'zipfile_validator',
    'twitter_name_validator', 'discord_name_validator',
    'reddit_name_validator'
]

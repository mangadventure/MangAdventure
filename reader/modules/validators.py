from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from zipfile import ZipFile, BadZipFile
from datetime import date
from io import BytesIO
from PIL import Image
from os import remove


def _remove_file(file):
    try:
        remove(file.path)
    except FileNotFoundError:
        pass


def is_dir(zipinfo):
    if hasattr(zipinfo, 'is_dir'):
        return zipinfo.is_dir()
    return zipinfo.filename.endswith('/')


class FileSizeValidator(BaseValidator):
    message = 'File too large. Maximum file size allowed is %(max)dMBs.'
    code = 'file_too_large'

    def __init__(self, max_mb=10):
        self.max_mb = max_mb
        super(FileSizeValidator, self).__init__(max_mb)

    def __call__(self, file):
        if file.size >= (self.max_mb * 1024 * 1024):
            _remove_file(file)
            raise ValidationError(
                message=self.message,
                code=self.code,
                params={'max': self.max_mb}
            )


def no_future_date(value):
    message = "Sorry. You can't send a chapter to the future."
    code = 'no_future_date'
    if value > date.today():
        raise ValidationError(
            message=message,
            code=code,
        )


def validate_zip_file(file):
    messages = [
        'The file must contain at most 1 subfolder.',
        'The file must not contain non-image files.',
        'The file must be in zip/cbz format.'
    ]
    codes = [
        'no_multiple_subfolders',
        'only_images', 'invalid_format'
    ]
    try:
        zip_file = ZipFile(file)
    except BadZipFile:
        _remove_file(file)
        raise ValidationError(
            message=messages[2],
            code=codes[2]
        )
    first_folder = True
    for f in zip_file.namelist():
        if is_dir(zip_file.getinfo(f)):
            if first_folder:
                first_folder = False
                continue
            _remove_file(file)
            raise ValidationError(
                message=messages[0],
                code=codes[0]
            )
        try:
            data = zip_file.read(f)
            img = Image.open(BytesIO(data))
            img.verify()
        except:
            _remove_file(file)
            raise ValidationError(
                message=messages[1],
                code=codes[1]
            )


__all__ = ['FileSizeValidator', 'no_future_date', 'validate_zip_file']


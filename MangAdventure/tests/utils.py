from hashlib import shake_128
from io import BytesIO
from os import urandom
from random import randint
from zipfile import ZipFile

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image


def get_test_image() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` for testing for FileFields.
    Taken from: https://stackoverflow.com/a/34276961

    :return: A dummy ``InMemoryUploadedFile``
    """
    im = Image.new(mode='RGB', size=(200, 200))
    im_io = BytesIO()
    im.save(im_io, 'PNG')
    im_io.seek(0)
    data = im_io.getvalue()
    sha = shake_128(data).hexdigest(16)
    return InMemoryUploadedFile(
        im_io, None, f'{sha}.png', 'image/png', len(data), None
    )


def get_valid_zip_file() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` of a valid zip file.

    :return: A dummy ``InMemoryUploadedFile``
    """
    file = BytesIO()
    with ZipFile(file, 'w') as zf:
        img_file = BytesIO()
        img = Image.new('RGB', size=(200, 200))
        img.save(img_file, 'JPEG')
        img_file.seek(0)
        zf.writestr('test/', '')
        zf.writestr('test/1.jpg', img_file.getvalue())
    file.seek(0)
    return InMemoryUploadedFile(
        file, None, 'file.zip', 'application/zip', len(file.getvalue()), None
    )


def get_multi_subdir_zip() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` of a zip file with more than one
    subdirectories.

    :return: A dummy ``InMemoryUploadedFile``
    """
    file = BytesIO()
    with ZipFile(file, 'w') as zf:
        img_file = BytesIO()
        img = Image.new('RGB', size=(200, 200))
        img.save(img_file, 'JPEG')
        img_file.seek(0)
        zf.writestr('test/', '')
        zf.writestr('test/folder/', '')
        zf.writestr('test/folder/1.jpg', img_file.getvalue())
    file.seek(0)
    return InMemoryUploadedFile(
        file, None, 'file.zip', 'application/zip', len(file.getvalue()), None
    )


def get_zip_with_invalid_images() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` of a zip file with invalid files.

    :return: A dummy ``InMemoryUploadedFile``
    """
    file = BytesIO()
    with ZipFile(file, 'w') as zf:
        zf.writestr('test/', '')
        zf.writestr('test/1.txt', 'test')
    file.seek(0)
    return InMemoryUploadedFile(
        file, None, 'file.zip', 'application/zip', len(file.getvalue()), None
    )


def get_random_file() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` of a random BytesIO file.

    :return: A dummy ``InMemoryUploadedFile``
    """
    file = BytesIO()
    file.write(urandom(randint(10, 2000)))
    file.seek(0)
    return InMemoryUploadedFile(
        file, None, 'file.zip', 'application/zip', len(file.getvalue()), None
    )

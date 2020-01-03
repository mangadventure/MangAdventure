from io import BytesIO
from os import urandom
from pathlib import Path
from random import randint
from shutil import rmtree
from zipfile import ZipFile

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import Client

import pytest
from PIL import Image

media_dir = Path(__file__).parent / 'media'


@pytest.mark.django_db
@pytest.mark.usefixtures('custom_test_settings')
class MangadvTestBase:
    def setup_class(self):
        media_dir.mkdir(exist_ok=True)

    def setup_method(self):
        self.client = Client()

    def teardown_method(self):
        pass

    def teardown_class(self):
        rmtree(media_dir)


def get_test_image() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` for testing for FileFields.
    Taken from: https://stackoverflow.com/a/34276961

    :return: A dummy ``InMemoryUploadedFile``
    """
    im = Image.new(mode='RGB', size=(200, 200))
    im_io = BytesIO()
    im.save(im_io, 'JPEG')
    im_io.seek(0)
    return InMemoryUploadedFile(im_io, None, 'random-name.jpg', 'image/jpeg',
                                len(im_io.getvalue()), None)


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
    return InMemoryUploadedFile(file, None, 'file.zip', 'application/zip',
                                len(file.getvalue()), None)


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
    return InMemoryUploadedFile(file, None, 'file.zip', 'zip/cbz',
                                len(file.getvalue()), None)


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
    return InMemoryUploadedFile(file, None, 'file.zip', 'zip/cbz',
                                len(file.getvalue()), None)


def get_random_file() -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` of a random BytesIO file.

    :return: A dummy ``InMemoryUploadedFile``
    """
    file = BytesIO()
    file.write(urandom(randint(10, 2000)))
    file.seek(0)
    return InMemoryUploadedFile(file, None, 'file.zip', 'zip/cbz',
                                len(file.getvalue()), None)

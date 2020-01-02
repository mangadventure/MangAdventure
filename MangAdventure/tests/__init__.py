from io import BytesIO
from zipfile import ZipFile

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import Client

import pytest
from PIL import Image


@pytest.mark.django_db
class MangadvTestBase:
    def setup_method(self):
        self.client = Client()


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


def get_big_image(mb_size: int = 3) -> InMemoryUploadedFile:
    """
    Get a dummy ``InMemoryUploadedFile`` of a specified megabyte size.

    :param mb_size: The size (in MB) of the file.

    :return: A dummy ``InMemoryUploadedFile``
    """
    file = BytesIO()
    file.seek((mb_size << 20) - 1)
    file.write(b'\0')
    file.seek(0)
    return InMemoryUploadedFile(file, None, 'big_file.jpg', 'image/jpeg',
                                len(file.getvalue()), None)


def get_valid_zip_file() -> InMemoryUploadedFile:
    """
        Get a dummy ``InMemoryUploadedFile`` of a valid zip size.

        :return: A dummy ``InMemoryUploadedFile``
        """
    file = BytesIO()
    with ZipFile(file, 'w') as zf:
        img_file = BytesIO()
        img = Image.new('RGB', size=(200, 200))
        img.save(img_file, 'JPEG')
        img_file.seek(0)
        zf.writestr('1.jpg', img_file.getvalue())
    file.seek(0)
    return InMemoryUploadedFile(file, None, 'file.zip', 'zip/cbz',
                                len(file.getvalue()), None)

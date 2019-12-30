from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

import pytest
from PIL import Image

from MangAdventure.tests import MangadvTestBase

from reader.models import Series


@pytest.mark.usefixtures("django_db_setup")
class UsersTestBase(MangadvTestBase):
    def setup_method(self):
        super().setup_method()
        self.series = Series.objects.get(pk=1)
        self.user = User.objects.get(pk=1)


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

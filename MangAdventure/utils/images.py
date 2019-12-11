"""Functions used to manipulate image files."""

from io import BytesIO
from os import path
from sys import getsizeof
from typing import Union

from django.core.files.uploadedfile import InMemoryUploadedFile
# XXX: Forward reference warning when under TYPE_CHECKING
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html

from PIL import Image

Image.MIME.setdefault('ICO', 'image/x-icon')


def thumbnail(obj: 'FieldFile', max_size: int = 100
              ) -> Union[InMemoryUploadedFile, 'FieldFile']:
    """
    Generate the thumbnail of an :class:`~django.db.models.ImageField`.

    :param obj: An ``ImageFieldFile`` instance.
    :param max_size: The width/height of the thumbnail.

    :return: The thumbnail, or the original if small enough.
    """
    if not path.exists(obj.path):
        return obj
    img = Image.open(obj.path)
    # Don't do anything if it's already a thumbnail
    if max_size in img.size:
        img.close()
        return obj
    # Convert grayscale images to RGB for better downsampling
    if img.mode in ('1', 'L', 'P'):
        img = img.convert('RGB')
        img.thumbnail((max_size, max_size), Image.ANTIALIAS)
        img = img.convert('P', dither=Image.NONE, palette=Image.ADAPTIVE)
    else:
        img.thumbnail((max_size, max_size), Image.ANTIALIAS)
    mime = Image.MIME.get(img.format)
    buff = BytesIO()
    img.save(buff, format=img.format, quality=100)
    buff.seek(0)
    obj.close()
    return InMemoryUploadedFile(
        buff, 'ImageField', obj.name, mime, getsizeof(buff), None
    )


def img_tag(obj: 'FieldFile', alt: str,
            height: int = 0, width: int = 0) -> str:
    """
    Create an HTML ``<img>`` from an :class:`~django.db.models.ImageField`.

    :param img: An ``ImageFieldFile`` instance.
    :param alt: The alternate text of the tag.
    :param height: The height of the ``<img>``. Unset if ``0``.
    :param width: The width of the ``<img>``. Unset if ``0``.

    :return: An ``<img>`` tag with the given image.
    """
    return format_html(
        '<img src="{0}" alt="{3}" width="{1}" height="{2}">',
        obj.url, width or '', height or '', alt or ''
    ) if hasattr(obj, 'url') else ''


__all__ = ['thumbnail', 'img_tag']

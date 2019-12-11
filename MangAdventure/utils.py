"""Various utility functions."""

from io import BytesIO
from os import path
from re import split
from sys import getsizeof
from typing import TYPE_CHECKING, List, Union

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import format_html

from PIL import Image

if TYPE_CHECKING:
    from django.db.models.fields.files import FieldFile


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
    Image.MIME.setdefault('ICO', 'image/x-icon')
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


def atoi(s: str) -> Union[int, str]:
    """Convert a :class:`str` to an :class:`int` if possible."""
    return int(s) if s.isdigit() else s.lower()


def alnum_key(k: str) -> List[str]:
    """Generate an alphanumeric key for sorting."""
    return list(map(atoi, split('([0-9]+)', k)))


def natsort(original: List[str]) -> List[str]:
    """
    Sort a list in natural order.

    .. code-block:: python

       >>> sorted(map(str, range(12)))
       ['0', '1', '10', '11', '2', '3', '4', '5', '6', '7', '8', '9']
       >>> natsort(map(str, range(12)))
       ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

    :param original: The original list.

    :return: The sorted list.

    .. seealso::

        https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    """
    return sorted(original, key=alnum_key)


__all__ = ['thumbnail', 'img_tag', 'natsort']

"""Template tags of the config app."""

from os.path import splitext
from typing import TYPE_CHECKING, List
from urllib.parse import urljoin as join
from urllib.request import urlopen

from django.template.defaultfilters import register, slice_filter

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


@register.filter
def urljoin(origin: str, pathname: str) -> str:
    """
    A template filter used to join URL parts.

    :param origin: The origin of the URL.
    :param pathname: The pathname of the URL.

    :return: The URL joined via :func:`~urllib.parse.urljoin`.
    """
    return join(origin, pathname)


@register.filter
def vslice(value: List, var: int) -> List:
    """
    Filter used to dynamically :tag:`slice` a list.

    :param value: The original list.
    :param var: The end of the slice.

    :return: The sliced list.
    """
    return slice_filter(value, f':{var:d}')


@register.filter
def order_by(qs: 'QuerySet', order: str) -> 'QuerySet':
    """
    Order a queryset by a given column.

    :param qs: The original queryset.
    :param order: The column used to order the queryset.

    :return: The ordered queryset.
    """
    return qs.order_by(order)


@register.filter
def get_type(link: str) -> str:
    """
    Get the type of an image given its URL.

    :param link: The link to the image file.

    :return: The mime type of the image.
    """
    try:
        with urlopen(link) as response:
            return response.info().get_content_type()
    except Exception:
        return {
            '.apng': 'image/png',
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
            '.ico': 'image/x-icon',
            '.icon': 'image/x-icon',
            '.j2k': 'image/jp2',
            '.jp2': 'image/jp2',
            '.jpeg': 'image/jpeg',
            '.jpf': 'image/jpx',
            '.jpg': 'image/jpeg',
            '.jpm': 'image/jpx',
            '.jpx': 'image/jpx',
            '.png': 'image/png',
            '.svg': 'image/svg+xml',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp'
        }.get(splitext(link.lower())[-1], 'image/jpeg')


__all__ = ['urljoin', 'vslice', 'order_by', 'get_type']

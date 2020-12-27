"""Various utility functions."""

from re import split
from typing import TYPE_CHECKING, Iterable, List, Union

from django.http import HttpResponse
from django.utils.html import format_html

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models.fields.files import FieldFile


class HttpResponseUnauthorized(HttpResponse):
    """
    A response class for HTTP :status:`401`.

    :param realm: The realm of the :header:`WWW-Authenticate` header.
    :type realm: str
    :param type: The type of the :header:`WWW-Authenticate` header.
    :type type: str
    """
    def __init__(self, *args, **kwargs):
        type_ = kwargs.pop('type', 'Bearer')
        realm = kwargs.pop('realm', 'private')
        super().__init__(*args, **kwargs)
        self['WWW-Authenticate'] = \
            f'{type_} realm="{realm}", charset="{self.charset}"'
        self.status_code = 401


def img_tag(obj: 'FieldFile', alt: str,
            height: int = 0, width: int = 0) -> str:
    """
    Create an HTML ``<img>`` from an :class:`~django.db.models.ImageField`.

    :param obj: An ``ImageFieldFile`` instance.
    :param alt: The alternate text of the tag.
    :param height: The height of the ``<img>``. Unset if ``0``.
    :param width: The width of the ``<img>``. Unset if ``0``.

    :return: An ``<img>`` tag with the given image.
    """
    return format_html(
        '<img src="{0}" alt="{3}" width="{1}" height="{2}">',
        obj.url, width or '', height or '', alt or ''
    ) if obj and hasattr(obj, 'url') else ''


def atoi(s: str) -> Union[int, str]:
    """Convert a :class:`str` to an :class:`int` if possible."""
    return int(s) if s.isdigit() else s.lower()


def alnum_key(k: str) -> List[Union[int, str]]:
    """Generate an alphanumeric key for sorting."""
    return list(map(atoi, split('([0-9]+)', k)))


def natsort(original: Iterable[str]) -> List[str]:
    """
    Sort a list in natural order.

    .. code-block:: python

       >>> sorted(map(str, range(12)))
       ['0', '1', '10', '11', '2', '3', '4', '5', '6', '7', '8', '9']
       >>> natsort(map(str, range(12)))
       ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

    :param original: The original iterable.

    :return: The sorted list.

    .. seealso::

        https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    """
    return sorted(original, key=alnum_key)


__all__ = ['HttpResponseUnauthorized', 'img_tag', 'natsort']

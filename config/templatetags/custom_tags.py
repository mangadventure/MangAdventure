"""Template tags of the config app."""

from json import dumps
from os.path import basename, splitext
from typing import Dict, List
from urllib.parse import urljoin as join
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import register, slice_filter
from django.utils.html import format_html
from django.utils.safestring import mark_safe


@register.filter
def urljoin(origin: str, pathname: str) -> str:
    """
    A template filter used to join URL parts.

    :param origin: The origin of the URL.
    :param pathname: The pathname of the URL.

    :return: The URL joined via :func:`~urllib.parse.urljoin`.
    """
    return join(origin, pathname)


@register.filter(is_safe=True)
def jsonld(value: Dict, element_id: str) -> str:
    """
    Generate a JSON-LD script tag.

    :param value: A JSON-LD dictionary.
    :param element_id: The id of the element.

    :return: An HTML ``<script>`` element.

    .. seealso:: :tag:`json_script template tag <json-script>`
    """
    sep = (',', ':')
    escapes = {ord('>'): '\\u003E', ord('<'): '\\u003C', ord('&'): '\\u0026'}
    jstr = dumps(value, cls=DjangoJSONEncoder, indent=None, separators=sep)
    return format_html(
        '<script id="{}" type="application/ld+json">{}</script>',
        element_id, mark_safe(jstr.translate(escapes))
    )


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
def get_type(link: str) -> str:
    """
    Get the type of an image given its URL.

    :param link: The link to the image file.

    :return: The mime type of the image.
    """
    if (key := 'type.' + basename(link.lower())) in cache:
        return cache.get(key)  # pragma: no cover
    try:
        with urlopen(Request(link, method='HEAD')) as response:
            type_ = response.info().get_content_type()
            cache.add(key, type_)
            return type_
    except Exception:
        return {
            '.apng': 'image/apng',
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
            '.heic': 'image/heic',
            '.heif': 'image/heif',
            '.ico': 'image/x-icon',
            '.icon': 'image/x-icon',
            '.j2k': 'image/jp2',
            '.jfif': 'image/jpeg',
            '.jls': 'image/jls',
            '.jp2': 'image/jp2',
            '.jpeg': 'image/jpeg',
            '.jpf': 'image/jpx',
            '.jpg': 'image/jpeg',
            '.jpm': 'image/jpm',
            '.jpx': 'image/jpx',
            '.jxl': 'image/jxl',
            '.jxr': 'image/jxr',
            '.jxs': 'image/jxs',
            '.png': 'image/png',
            '.svg': 'image/svg+xml',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp'
        }.get(splitext(link.lower())[-1], 'image/jpeg')


__all__ = ['urljoin', 'vslice', 'jsonld', 'get_type']

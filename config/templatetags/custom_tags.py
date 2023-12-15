"""Template tags of the config app."""

from json import dumps
from urllib.parse import urljoin as join

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
def jsonld(value: dict, element_id: str) -> str:
    """
    Generate a JSON-LD script tag.

    :param value: A JSON-LD dictionary.
    :param element_id: The id of the element.

    :return: An HTML ``<script>`` element.

    .. seealso:: :tag:`json_script template tag <json-script>`
    """
    sep = (',', ':')
    # Escape special HTML characters for JSON output
    escapes = {ord('>'): '\\u003E', ord('<'): '\\u003C', ord('&'): '\\u0026'}
    jstr = dumps(value, cls=DjangoJSONEncoder, indent=None, separators=sep)
    return format_html(
        '<script id="{}" type="application/ld+json">{}</script>',
        element_id, mark_safe(jstr.translate(escapes))  # nosec: B308
    )


@register.filter
def vslice(value: list, var: int) -> list:
    """
    Filter used to dynamically :tag:`slice` a list.

    :param value: The original list.
    :param var: The end of the slice.

    :return: The sliced list.
    """
    return slice_filter(value, f':{var:d}')


__all__ = ['urljoin', 'vslice', 'jsonld']

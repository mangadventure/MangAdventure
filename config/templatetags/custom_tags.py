from os.path import basename, splitext
from urllib.parse import urljoin as join
from urllib.request import urlopen

from django.template.defaultfilters import register, slice_filter


@register.filter
def urljoin(origin, pathname):
    return join(origin, pathname)


@register.filter
def vslice(value, var):
    return slice_filter(value, f':{var:d}')


@register.filter
def order_by(qs, order):
    return qs.order_by(order)


@register.filter
def get_name(value):
    return basename(value)


@register.filter
def get_ext(value):
    return splitext(value)[-1]


@register.filter
def get_type(link):
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

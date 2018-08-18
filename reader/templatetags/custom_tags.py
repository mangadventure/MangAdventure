from django.template.defaultfilters import register, slice_filter
from urllib.parse import urljoin as join
from urllib.request import urlopen
from os.path import splitext, basename
from re import sub


@register.filter
def unquote(value): return sub(r'^["\']|["\']$', '', value)


@register.filter
def urljoin(origin, pathname): return join(origin, pathname)


@register.filter
def vslice(value, var): return slice_filter(value, ':%s' % var)


@register.filter
def order_by(value, order): return value.order_by(order)


@register.filter
def get_name(value): return basename(value)


@register.filter
def get_ext(value): return splitext(value)[-1]


@register.filter
def get_type(link):
    try:
        with urlopen(link) as response:
            return response.info().get_content_type()
    except:
        ext = splitext(link.lower())[-1]
        return {
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.icon': 'image/x-icon',
            '.webp': 'image/webp',
            '.apng': 'image/apng',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.pic': 'image/pict',
            '.pict': 'image/pict'
        }.get(ext, 'image/jpeg')


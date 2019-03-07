from django.template.defaultfilters import register, slice_filter
from django.utils.six import moves
from os.path import splitext, basename

join = moves.urllib.parse.urljoin
urlopen = moves.urllib.request.urlopen


@register.filter
def urljoin(origin, pathname): return join(origin, pathname)


@register.filter
def vslice(value, var): return slice_filter(value, ':%d' % var)


@register.filter
def order_by(qs, order): return qs.order_by(order)


@register.filter
def get_name(value): return basename(value)


@register.filter
def get_ext(value): return splitext(value)[-1]


@register.filter
def get_type(link):
    try:
        with urlopen(link) as response:
            return response.info().get_content_type()
    except Exception:
        return {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.icon': 'image/x-icon',
            '.apng': 'image/apng',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.pic': 'image/pict',
            '.pict': 'image/pict'
        }.get(splitext(link.lower())[-1], 'image/jpeg')


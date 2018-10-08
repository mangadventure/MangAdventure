from django.template.defaultfilters import register, slice_filter
from django.contrib.staticfiles.finders import find
from django.utils.six import moves
from os.path import splitext, basename
from base64 import b64encode
from hashlib import sha256
from re import sub

join = moves.urllib.parse.urljoin
urlopen = moves.urllib.request.urlopen


@register.filter
def unquote(value): return sub(r'^["\']|["\']$', '', value)


@register.filter
def urljoin(origin, pathname): return join(origin, pathname)


@register.filter
def vslice(value, var): return slice_filter(value, ':%s' % var)


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


@register.simple_tag
def sha256hash(sfile):
    BUF_SIZE = 4096
    hash = sha256()
    with open(find(sfile), 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hash.update(data)
    b64 = b64encode(hash.digest()).decode()
    return 'sha256-%s' % b64


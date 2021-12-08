"""
Custom storages.

.. seealso::

    https://docs.djangoproject.com/en/3.2/ref/files/storage/
"""

from typing import Optional, Tuple
from urllib.parse import quote

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CDNStorage(FileSystemStorage):
    """
    Storage class that may use an image CDN.

    The options are statically_, weserv_ & photon_.

    :param fit: A tuple of width & height to fit the image in.

    .. _statically: https://statically.io/docs/using-images/
    .. _weserv: https://images.weserv.nl/docs/
    .. _photon: https://developer.wordpress.com/docs/photon/
    """
    def __init__(self, fit: Optional[Tuple[int, int]] = None):
        super().__init__()
        self._cdn = settings.CONFIG['USE_CDN'].lower()
        self._fit = {'w': fit[0], 'h': fit[1]} if fit else {}

    def _statically_url(self, name: str) -> str:
        domain = settings.CONFIG['DOMAIN']
        base = f'https://cdn.statically.io/img/{domain}/'
        fit = ','.join('%s=%d' % i for i in self._fit.items())
        return base + fit + self.base_url + name

    def _weserv_url(self, name: str) -> str:
        domain = settings.CONFIG['DOMAIN']
        base = 'https://images.weserv.nl/?url='
        scheme = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        url = f'{scheme}://{domain}{self.base_url}{name}'
        params = {**self._fit, 'l': 0, 'q': 100}
        qs = '&'.join('%s=%d' % i for i in params.items())
        return base + quote(url, '') + '&' + qs + '&we'

    def _photon_url(self, name: str) -> str:
        domain = settings.CONFIG['DOMAIN']
        scheme = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        base, qs = f'{scheme}://i3.wp.com/', '?quality=100'
        if self._fit:
            qs += f'&fit={self._fit["w"]},{self._fit["h"]}'
        return base + domain + self.base_url + name + qs

    def url(self, name: str) -> str:
        """
        Return the URL where the contents of the file
        referenced by ``name`` can be accessed.

        :param name: The name of the file.

        :return: The URL of the file.
        """
        method = f'_{self._cdn}_url'
        if not hasattr(self, method):
            return super().url(name)
        return getattr(self, method)(name)


__all__ = ['CDNStorage']

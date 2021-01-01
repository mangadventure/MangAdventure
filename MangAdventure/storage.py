"""
Custom storages.

.. seealso::

    https://docs.djangoproject.com/en/3.1/ref/files/storage/
"""

from typing import Optional, Tuple
from urllib.parse import urlencode

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CDNStorage(FileSystemStorage):
    """
    Storage class that uses the `statically image CDN`_ unless
    :const:`~MangAdventure.settings.DEBUG` mode is on.

    :param fit: A tuple of width & height to fit the image in.

    .. _`statically image CDN`:
        https://statically.io/images/
    """
    def __init__(self, fit: Optional[Tuple[int, int]] = None):
        site = settings.CONFIG['DOMAIN']
        self._nocdn = not settings.CONFIG['USE_CDN'] or settings.DEBUG
        if self._nocdn:  # pragma: no cover
            return super(CDNStorage, self).__init__()
        cdn = 'https://cdn.statically.io/img/'
        url = cdn + site + settings.MEDIA_URL
        super(CDNStorage, self).__init__(base_url=url)
        self._fit = f'{fit[0]},{fit[1]}' if fit else None

    def url(self, name: str) -> str:
        """
        Return the URL where the contents of the file
        referenced by ``name`` can be accessed.

        :param name: The name of the file.

        :return: The URL of the file.
        """
        if self._nocdn:  # pragma: no cover
            return super(CDNStorage, self).url(name)
        try:
            time = self.get_modified_time(name)
            qs = {'t': f'{time.timestamp():.0f}'}
        except NotImplementedError:  # pragma: no cover
            qs = {}
        if self._fit:
            qs['fit'] = self._fit
        if name.lower().endswith(('.jpg', '.jpeg', '.jfif')):
            qs.update({'quality': '100', 'strip': 'all'})
        return f'{self.base_url}{name}?{urlencode(qs, safe=",")}'

    def get_available_name(self, name: str, max_length:
                           Optional[int] = None) -> str:
        """
        Return a filename that's free on the target storage system.

        If a file with the given name exists, it will be deleted.

        :param name: The desired filename.
        :param max_length: The maximum length of the name. *(unused)*

        :return: The available filename.
        """
        if self.exists(name):
            self.delete(name)
        return name


__all__ = ['CDNStorage']

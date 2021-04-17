"""
Custom storages.

.. seealso::

    https://docs.djangoproject.com/en/3.1/ref/files/storage/
"""

from typing import Optional, Tuple

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
        super().__init__()
        if settings.CONFIG['USE_CDN'] and not settings.DEBUG:
            self._cdn = 'https://cdn.statically.io/img/'
            self.base_url = self._cdn + settings.CONFIG['DOMAIN']
            self._params = {'w': fit[0], 'h': fit[1]} if fit else {}

    def url(self, name: str) -> str:
        """
        Return the URL where the contents of the file
        referenced by ``name`` can be accessed.

        :param name: The name of the file.

        :return: The URL of the file.
        """
        if not hasattr(self, '_cdn'):  # pragma: no cover
            return super().url(name)
        url = self.base_url + '/{}' + settings.MEDIA_URL + '{}{}'
        try:
            time = self.get_modified_time(name)
            qs = f'?t={time.timestamp():.0f}'
        except NotImplementedError:  # pragma: no cover
            qs = ''
        if name.lower().endswith(('.jpg', '.jpeg', '.jfif')):
            self._params['q'] = 100
        return url.format(
            ','.join('%s=%d' % i for i in self._params.items()), name, qs
        )

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

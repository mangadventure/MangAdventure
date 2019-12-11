"""
Custom storages.

.. seealso::

    https://docs.djangoproject.com/en/3.0/ref/files/storage/
"""
from typing import Optional

from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """Storage class that allows overwriting files."""
    def get_available_name(self, name: str, max_length:
                           Optional[int] = None) -> str:
        """
        Return a filename that's free on the target storage system and
        available for new content to be written to.

        :param name: The desired filename.
        :param max_length: The maximum length of the name. *(unused)*

        :return: The available filename.
        """
        # If the file already exists, remove it
        if self.exists(name):
            self.delete(name)
        return name


__all__ = ['OverwriteStorage']

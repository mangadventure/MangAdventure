from os import path, remove

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        # If the file already exists, remove it
        if self.exists(name):
            remove(path.join(settings.MEDIA_ROOT, name))
        return name


__all__ = ['OverwriteStorage']

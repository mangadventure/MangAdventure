from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        # If the file already exists, remove it
        if self.exists(name):
            (settings.MEDIA_ROOT / name).unlink()
        return name


__all__ = ['OverwriteStorage']

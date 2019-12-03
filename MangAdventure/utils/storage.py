from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        # If the file already exists, remove it
        old_file = settings.MEDIA_ROOT / name
        if old_file.exists():
            old_file.unlink()
        return name


__all__ = ['OverwriteStorage']

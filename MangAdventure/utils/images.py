from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from os import path, remove, makedirs
from zipfile import ZipFile
from sys import getsizeof
from io import BytesIO
from PIL import Image
from . import is_dir, sort


def thumbnail(obj, max_size=100):
    img = Image.open(obj)
    img.thumbnail((max_size, max_size), Image.ANTIALIAS)
    Image.MIME.setdefault('ICO', 'image/x-icon')
    mime = Image.MIME.get(img.format)
    buff = BytesIO()
    img.save(buff, format=img.format, quality=100)
    buff.seek(0)
    return InMemoryUploadedFile(buff, 'ImageField',
                                obj.name, mime,
                                getsizeof(buff), None)


def unzip(obj):
    counter = 0
    zip_file = ZipFile(obj.file)
    name_list = zip_file.namelist()
    for name in sort.natural_sort(name_list):
        if is_dir(zip_file.getinfo(name)):
            continue
        counter += 1
        data = zip_file.read(name)
        filename = '%03d%s' % (counter, path.splitext(name)[-1])
        file_path = path.join(
            'series',
            obj.series.slug,
            str(obj.volume),
            str(obj.number),
            filename
        )
        full_path = path.join(settings.MEDIA_ROOT, file_path)
        if not path.exists(path.dirname(full_path)):
            makedirs(path.dirname(full_path))
        if path.exists(full_path):
            remove(full_path)
        image = Image.open(BytesIO(data))
        image.save(full_path, optimize=True, quality=100)
        obj.pages.create(number=counter, image=file_path)
    zip_file.close()
    # TODO: option to keep zip file
    remove(obj.file.path)
    obj.file.delete(save=True)


__all__ = ['thumbnail', 'unzip']


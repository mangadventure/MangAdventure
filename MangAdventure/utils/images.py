from io import BytesIO
from os import makedirs, path, remove
from shutil import rmtree
from sys import getsizeof
from zipfile import ZipFile

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import format_html

from PIL import Image

from . import sort

Image.MIME.setdefault('ICO', 'image/x-icon')


def _is_dir(f):
    return f.filename[-1] == '/'


def thumbnail(obj, max_size=100):
    try:
        img = Image.open(obj)
    except OSError as e:
        if e.errno == 2:
            return obj
        else:
            raise e
    # Don't do anything if it's already a thumbnail
    if max_size in img.size:
        img.close()
        return obj
    # Convert grayscale images to RGB for better downsampling
    if img.mode in ('1', 'L', 'P'):
        img = img.convert('RGB')
        img.thumbnail((max_size, max_size), Image.ANTIALIAS)
        img = img.convert('P', dither=Image.NONE, palette=Image.ADAPTIVE)
    else:
        img.thumbnail((max_size, max_size), Image.ANTIALIAS)
    mime = Image.MIME.get(img.format)
    buff = BytesIO()
    img.save(buff, format=img.format, quality=100)
    buff.seek(0)
    obj.close()
    return InMemoryUploadedFile(
        buff, 'ImageField', obj.name, mime, getsizeof(buff), None
    )


def img_tag(img, alt, height=None, width=None):
    return format_html(
        '<img src="{0}" alt="{3}" width="{1}" height="{2}">',
        img.url, width or '', height or '', alt or ''
    ) if hasattr(img, 'url') else ''


def unzip(obj):
    counter = 0
    dir_path = path.join(
        'series', obj.series.slug, str(obj.volume), '%g' % obj.number
    )
    full_path = path.join(settings.MEDIA_ROOT, dir_path)
    if path.exists(full_path):
        rmtree(full_path)
    makedirs(full_path)
    zip_file = ZipFile(obj.file)
    name_list = zip_file.namelist()
    for name in sort.natural_sort(name_list):
        if _is_dir(zip_file.getinfo(name)):
            continue
        counter += 1
        data = zip_file.read(name)
        filename = '%03d%s' % (counter, path.splitext(name)[-1])
        file_path = path.join(dir_path, filename)
        image = Image.open(BytesIO(data))
        image.save(path.join(full_path, filename), quality=100)
        obj.pages.create(number=counter, image=file_path)
    zip_file.close()
    obj.file.close()
    # TODO: option to keep zip file
    remove(obj.file.path)
    obj.file.delete(save=True)


__all__ = ['thumbnail', 'img_tag', 'unzip']

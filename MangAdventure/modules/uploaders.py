from os.path import splitext, join


def _rename_file(old, new): return new + splitext(old)[-1]


def _uploader(filename, newname, subdirs):
    return join(join(*subdirs), _rename_file(filename, newname))


def cover_uploader(instance, filename):
    return _uploader(filename, 'cover', ['series', instance.slug])


def group_logo_uploader(instance, filename):
    return _uploader(filename, 'logo', ['groups', instance.id])


def member_avatar_uploader(instance, filename):
    return _uploader(filename, 'avatar', ['members', instance.id])


__all__ = ['cover_uploader', 'group_logo_uploader', 'member_avatar_uploader']


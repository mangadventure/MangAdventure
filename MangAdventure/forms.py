from io import BytesIO
from json import dumps
from sys import exc_info
from xml.etree import cElementTree as et

from django.core.exceptions import ValidationError
from django.forms import CharField, ImageField, URLField, Widget, widgets
from django.utils.six import reraise

from PIL import Image

from MangAdventure.utils import validators


# Source: https://gist.github.com/ambivalentno/9bc42b9a417677d96a21
class SVGImageField(ImageField):

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a
        valid image (GIF, JPG, PNG, possibly others --
        whatever the Python Imaging Library supports).
        """
        test_file = super(ImageField, self).to_python(data)
        if test_file is None:
            return None

        # We need to get a file object for Pillow.
        # We might have a path or we might
        # have to read the data into memory.
        if hasattr(data, 'temporary_file_path'):
            ifile = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                ifile = BytesIO(data.read())
            else:
                ifile = BytesIO(data['content'])

        try:
            # load() could spot a truncated JPEG, but it loads the entire
            # image in memory, which is a DoS vector. See #3848 and #18520.
            image = Image.open(ifile)
            # verify() must be called immediately after the constructor.
            image.verify()

            # Annotating so subclasses can reuse it for their own validation
            test_file.image = image
            test_file.content_type = Image.MIME[image.format]
        except OSError:
            # add a workaround to handle svg images
            if not self.is_svg(ifile):
                reraise(ValidationError, ValidationError(
                    self.error_messages['invalid_image'],
                    code='invalid_image',
                ), exc_info()[2])
        if hasattr(test_file, 'seek') and callable(test_file.seek):
            test_file.seek(0)
        return test_file

    def run_validators(self, value):
        if self.is_svg(value):
            return
        super(ImageField, self).run_validators(value)

    @staticmethod
    def is_svg(f):
        """
        Check if provided file is svg
        """
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        else:
            f = open(f, 'r')
        try:
            tag = '{http://www.w3.org/2000/svg}svg'
            iter = et.iterparse(f, ('start',))
            return next(iter)[1].tag == tag
        except et.ParseError:
            return False


class ColorField(CharField):
    def __init__(self, *args, **kwargs):
        self.min_length = 7
        self.max_length = 20
        self.strip = True
        super(CharField, self).__init__(*args, **kwargs)
        self.widget = widgets.TextInput({'type': 'color'})


class TwitterField(CharField):
    default_validators = [validators.twitter_name_validator]

    def __init__(self, *args, **kwargs):
        super(TwitterField, self).__init__(*args, **kwargs)


class DiscordURLField(URLField):
    default_validators = [validators.discord_server_validator]

    def __init__(self, **kwargs):
        super(DiscordURLField, self).__init__(**kwargs)


class TinyMCE(Widget):
    template_name = 'django/forms/widgets/textarea.html'

    def __init__(self, attrs=None):
        attrs = attrs or {}
        if 'class' in attrs:
            attrs['class'] += ' tinymce'
        else:
            attrs['class'] = 'tinymce'
        attrs.update({'cols': '75', 'rows': '15'})
        mce_attrs = {
            'selector': '.tinymce',
            'theme': 'modern',
            'relative_urls': True
        }
        for key in list(attrs):
            if key.startswith('mce_'):
                mce_attrs[key[4:]] = attrs.pop(key)
        attrs['data-tinymce-config'] = dumps(mce_attrs)
        super(TinyMCE, self).__init__(attrs)

    class Media:
        extend = False
        js = (
            'https://cdn.tinymce.com/4/tinymce.min.js',
            'scripts/tinymce-init.js'
        )


__all__ = [
    'SVGImageField', 'TwitterField',
    'DiscordURLField', 'ColorField', 'TinyMCE',
]

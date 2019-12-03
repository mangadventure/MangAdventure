from io import BytesIO
from xml.etree import cElementTree as et

from django.core.exceptions import ValidationError
from django.forms import CharField, ImageField, URLField

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
        elif hasattr(data, 'read'):
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
        except OSError as err:
            # add a workaround to handle svg images
            if not self.is_svg(ifile):
                raise ValidationError(
                    self.error_messages['invalid_image'],
                    code='invalid_image',
                ) from err
        if hasattr(test_file, 'seek') and callable(test_file.seek):
            test_file.seek(0)
        return test_file

    def run_validators(self, value):
        if not self.is_svg(value):
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


class TwitterField(CharField):
    default_validators = (validators.twitter_name_validator,)


class DiscordURLField(URLField):
    default_validators = (validators.discord_server_validator,)


__all__ = ['SVGImageField', 'TwitterField', 'DiscordURLField']

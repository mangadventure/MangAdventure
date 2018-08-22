from django.core.exceptions import ValidationError
from django.forms import ImageField
from django.utils.six import reraise
from xml.etree import cElementTree as et
from sys import exc_info
from io import BytesIO
from PIL import Image


class SVGImageField(ImageField):

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF, JPG,
        PNG, possibly others -- whatever the Python Imaging Library supports).
        """
        test_file = super(ImageField, self).to_python(data)
        if test_file is None:
            return None

        # We need to get a file object for Pillow. We might have a path or we might
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
        f.seek(0)
        tag = None
        try:
            for event, el in et.iterparse(f, ('start',)):
                tag = el.tag
                break
        except et.ParseError:
            pass
        return tag == '{http://www.w3.org/2000/svg}svg'


__all__ = ['SVGImageField']

# Source: https://gist.github.com/ambivalentno/9bc42b9a417677d96a21


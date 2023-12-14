"""Custom form widgets."""

from json import dumps

from django.forms import Textarea


class TinyMCE(Textarea):
    """
    A textarea :class:`~django.forms.Widget`
    for `TinyMCE <https://www.tiny.cloud/>`_.

    :param attrs: A dictionary of the widget's attributes.
    """

    def __init__(self, attrs: dict[str, str] = {}):
        if 'class' in attrs:  # pragma: no cover
            attrs['class'] += ' tinymce'
        else:
            attrs['class'] = 'tinymce'
        attrs |= {'cols': '75', 'rows': '15'}
        mce_attrs = {
            'selector': '.tinymce',
            'theme': 'modern',
            'relative_urls': True
        }
        for key in list(attrs):
            if key.startswith('mce_'):
                mce_attrs[key[4:]] = attrs.pop(key)
        attrs['data-tinymce-config'] = dumps(mce_attrs)
        super().__init__(attrs)

    class Media:
        extend = False
        js = (
            'https://cdn.jsdelivr.net/npm/tinymce@4.9.11/tinymce.min.js',
            'scripts/tinymce-init.js'
        )


__all__ = ['TinyMCE']

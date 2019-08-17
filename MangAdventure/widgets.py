from json import dumps

from django.forms import Widget


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


__all__ = ['TinyMCE']

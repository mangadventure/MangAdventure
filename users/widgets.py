"""Form widgets for the users app."""

from django.conf import settings

from MangAdventure.widgets import TinyMCE

#: A :class:`~MangAdventure.widgets.TinyMCE` widget used in comments.
TinyMCEComment = TinyMCE(attrs={
    'mce_theme': 'modern',
    'mce_resize': False,
    'mce_menubar': False,
    'mce_replace_icons': True,
    'mce_plugins': 'save lists advlist link image',
    'mce_toolbar': ' | '.join([
        'save', 'undo redo', 'cut copy paste',
        'formatselect', 'alignleft aligncenter alignright',
        'bold italic underline strikethrough blockquote',
        'bullist numlist', 'link unlink image'
    ]),
    'mce_content_css': [
        settings.STATIC_URL + 'COMPILED/styles/tinymce.css'
    ]
})

__all__ = ['TinyMCEComment']

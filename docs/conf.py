# -- Setup Django --

from sys import path
from os import environ as env
from os.path import dirname

path.insert(0, dirname(__file__))
env['DJANGO_SETTINGS_MODULE'] = 'MangAdventure.tests.settings'
__import__('django').setup()


# -- Project information --

import MangAdventure as MA

project = 'MangAdventure'
author = MA.__author__
release = MA.__version__
copyright = f'2018-2020, {project}, {MA.__license__} license'


# -- Add setup function & patch documenters --

from typing import get_type_hints, Any, List, Optional, Type, Tuple

from django.db.models.fields.related_descriptors import (
    ReverseManyToOneDescriptor, ReverseOneToOneDescriptor,
)
from django.db.models.query_utils import DeferredAttribute

from sphinx.application import Sphinx
from sphinx.ext.autodoc import DataDocumenter, Options, PropertyDocumenter


def skip_django_junk(app: Sphinx, what: str, name: str,
                     obj: Any, skip: bool, options: Options) -> bool:
    junk = (
        DeferredAttribute,
        ReverseManyToOneDescriptor,
        ReverseOneToOneDescriptor,
    )
    if isinstance(obj, junk):
        return True
    if isinstance(obj, property) and name == 'media':
        return True
    return skip

def annotate_attributes(app: Sphinx, what: str, name: str,
                        obj: Any, options: Options, lines: List[str]):

    if obj is None or not lines:
        return
    if what == 'attribute':
        cls = getattr(obj, 'field', obj).__class__
    elif what == 'property':
        func = obj.func if hasattr(obj, 'func') else obj.fget
        cls = get_type_hints(func)['return']
    else:
        return
    mod = cls.__module__
    if mod == 'builtins':
        qname = cls.__name__
    elif mod.startswith('django.db.models'):
        qname = f'django.db.models.{cls.__name__}'
    else:
        qname = f'{mod}.{cls.__name__}'
    if qname in ('dict', 'list', 'tuple'):
        qname = f'typing.{qname.capitalize()}'
    lines[0] = f':class:`~{qname}` – {lines[0]}'

def setup(app: Sphinx):
    app.connect('autodoc-skip-member', skip_django_junk)
    app.connect('autodoc-process-docstring', annotate_attributes)
    app.add_stylesheet('css/style.css')

PropertyDocumenter._original_can_document_member = \
    PropertyDocumenter.can_document_member

def _patched_can_document_member(cls: Type[PropertyDocumenter],
                                 member: Any, membername: str,
                                 isattr: bool, parent: Any) -> bool:
    return member.__class__.__name__ == 'cached_property' or \
        cls._original_can_document_member(member, membername, isattr, parent)

PropertyDocumenter.can_document_member = \
    classmethod(_patched_can_document_member)

DataDocumenter._original_add_directive_header = \
    DataDocumenter.add_directive_header

def _patched_add_directive_header(self: DataDocumenter, sig: str):
    # Don't document values of settings
    if self.modname == 'MangAdventure.settings':
        DataDocumenter.__base__.add_directive_header(self, sig)
    else:
        self._original_add_directive_header(sig)

DataDocumenter.add_directive_header = _patched_add_directive_header


# -- General configuration --

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
pygments_style = 'manni'


# -- InterSphinx & extlinks configuration --

_django = 'https://docs.djangoproject.com/en/3.0/'
_mdn = 'https://developer.mozilla.org/en-US/docs/Web/'

intersphinx_mapping = {
    'django': (_django, f'{_django}_objects/'),
    'python': ('https://docs.python.org/3.6/', None),
}

extlinks = {
    'setting': (f'{_django}ref/settings/#std:setting-%s', ''),
    'tag': (f'{_django}ref/templates/builtins/#%s', ''),
    'auth': ('https://django-allauth.rtfd.io/en/latest/%s', ''),
    'csp': (f'{_mdn}HTTP/Headers/Content-Security-Policy/%s', ''),
    'status': (f'{_mdn}HTTP/Status/%s', ''),
    'schema': ('https://schema.org/%s', ''),
}


# -- Autodoc configuration --

autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': True,
    'undoc-members': True,
    'exclude-members': ','.join((
        '__dict__',
        '__init__',
        '__slots__',
        '__module__',
        '__weakref__',
        '__slotnames__',
        '__annotations__',
    ))
}
autodoc_inherit_docstrings = True
always_document_param_types = True
set_type_checking_flag = True
typehints_fully_qualified = False
typehints_document_rtype = True


# -- Options for HTML output --

html_theme = 'sphinx_rtd_theme'
html_theme_path = [__import__(html_theme).get_html_theme_path()]
html_theme_options = {
    'logo_only': True,
    'display_version': False,
    'collapse_navigation': True,
}
html_static_path = ['_static']
html_logo = '_static/logo.png'
# html_sidebars = {}


# -- Options for HTMLHelp output --

htmlhelp_basename = f'{project}Doc'


# -- Options for LaTeX output --

latex_elements = {}
latex_documents = [(
    master_doc, f'{project}.tex',
    f'{project} Documentation', author, 'manual'
)]


# -- Options for manual page output --

man_pages = [(
    master_doc, project.lower(),
    f'{project} Documentation', author.split(', '), 7
)]


# -- Options for Texinfo output --

texinfo_documents = [(
    master_doc, project, f'{project} Documentation',
    author, project, MA.__doc__, 'Miscellaneous'
)]

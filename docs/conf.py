# -- Setup Django --

from os import environ as env
from os.path import dirname, join
from sys import path

path.insert(0, dirname(dirname(__file__)))
path.insert(1, join(dirname(__file__), '_ext'))
env['DJANGO_SETTINGS_MODULE'] = 'MangAdventure.tests.settings'
__import__('django').setup()


# -- Project information --

import MangAdventure as MA  # noqa: E402

project = 'MangAdventure'
author = MA.__author__
release = MA.__version__
copyright = f'2018-2022, {project}, {MA.__license__} license'


# -- General configuration --

extensions = [
    'sphinx.ext.autodoc',
    'mangadventure_patches',
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
needs_sphinx = '4.3'


# -- InterSphinx & extlinks configuration --

_django = 'https://docs.djangoproject.com/en/3.2/'
_mdn = 'https://developer.mozilla.org/en-US/docs/Web/'

intersphinx_mapping = {
    'django': (_django, f'{_django}_objects/'),
    'python': ('https://docs.python.org/3.7/', None),
}

extlinks = {
    'setting': (f'{_django}ref/settings/#std:setting-%s', ''),
    'tag': (f'{_django}ref/templates/builtins/#%s', ''),
    'auth': ('https://django-allauth.rtfd.io/en/latest/%s', ''),
    'csp': (f'{_mdn}HTTP/Headers/Content-Security-Policy/%s', ''),
    'status': (f'{_mdn}HTTP/Status/%s', ''),
    'header': (f'{_mdn}HTTP/Headers/%s', ''),
    'schema': ('https://schema.org/%s', ''),
}


# -- Autodoc configuration --

autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': True,
    'undoc-members': True,
    'exclude-members': ','.join((
        '__new__',
        '__dict__',
        '__repr__',
        '__init__',
        '__slots__',
        '__module__',
        '__weakref__',
        '__slotnames__',
        '__annotations__',
    ))
}
autodoc_mock_imports = ['pytest']
autodoc_inherit_docstrings = True
always_document_param_types = True
set_type_checking_flag = True
typehints_fully_qualified = False
typehints_document_rtype = True
# disable sphinx.ext.autodoc.typehints
autodoc_typehints = 'none'


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

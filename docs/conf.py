# -- Path setup --

import os
import sys
import django
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MangAdventure.settings')
django.setup()

# -- Project information --

project = 'MangAdventure'
copyright = '2018, Evangelos Ch - MIT License'
author = 'evangelos-ch, ObserverOfTime'

from MangAdventure import __version__ as version
release = version


# -- General configuration --

extensions = [
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store',
                    'desktop.ini', '.directory']
pygments_style = 'manni'


# -- Custom CSS --

def setup(app): app.add_stylesheet('css/style.css')


# -- Options for HTML output --

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'display_version': False,
    'collapse_navigation': True,
}
html_static_path = ['_static']
# html_sidebars = {}


# -- Options for HTMLHelp output --

htmlhelp_basename = 'MangAdventureDoc'


# -- Options for LaTeX output --

latex_elements = {}
latex_documents = [
    (master_doc, 'MangAdventure.tex',
     'MangAdventure Documentation',
     'evangelos-ch, ObserverOfTime', 'manual'),
]


# -- Options for manual page output --

man_pages = [
    (master_doc, 'mangadventure',
     'MangAdventure Documentation',
     [author], 7)
]


# -- Options for Texinfo output --

texinfo_documents = [
    (master_doc, 'MangAdventure', 'MangAdventure Documentation',
     author, 'MangAdventure', 'A simple manga hosting webapp'
     ' written in Django.', 'Miscellaneous'),
]


# -- Project information --

import MangAdventure as MA

project = 'MangAdventure'
author = MA.__author__
release = MA.__version__
copyright = f'2018-2020, {project}, {MA.__license__} license'


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
pygments_style = 'manni'


# -- Custom CSS --

def setup(app):
    app.add_stylesheet('css/style.css')


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

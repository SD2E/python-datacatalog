# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import string
import urllib.parse
from tabulate import tabulate

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))

from datacatalog.jsonschemas.schema import JSONSchemaBaseObject
from datacatalog.linkedstores.pipelinejob import fsm as pipelinejob_fsm
from datacatalog.identifiers import typeduuid
from datacatalog.tokens import get_admin_lifetime
from datacatalog.views.aggregations import get_aggregations

from datacatalog import __version__ as code_version
from datacatalog import __schema_version__ as schema_version_tuple
from datacatalog import __schema_major_version__ as schema_major_version
from datacatalog import __jsonschema_version__ as jsonschema_version

def rstjinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    # Make sure we're outputting HTML
    if app.builder.format != 'html':
        return
    src = source[0]
    rendered = app.builder.templates.render_string(
        src, app.config.html_context
    )
    source[0] = rendered

def setup(app):
    app.connect("source-read", rstjinja)

def table_pipelinejob_states():
    return tabulate(pipelinejob_fsm.STATE_DEFS, ['State', 'Description'], tablefmt='rst')

def table_pipelinejob_events():
    return tabulate(pipelinejob_fsm.EVENT_DEFS, ['Event', 'Description'], tablefmt='rst')

def opt_admin_token_lifetime():
    return str(get_admin_lifetime())

def table_typeduuid_types():
    return tabulate(typeduuid.UUIDTYPES, ['Type', 'Prefix', 'Description'], tablefmt='rst')

def text_schema_version():
    return '.'.join(list(schema_version_tuple))

def text_jsonschema_version():
    return urllib.parse.quote(jsonschema_version)

def table_views():
    view_rows = list()
    for k, v in get_aggregations().items():
        row = [k, v.description, v.view_on, v.author]
        view_rows.append(row)
    return tabulate(view_rows, ['Name', 'Description', 'Source', 'Author'], tablefmt='rst')


html_context = {
    'css_files': ['_static/theme_overrides.css'],
    'project_schema_base_url': JSONSchemaBaseObject.BASEREF,
    'project_schema_browser_url': 'https://browser.catalog.sd2e.org',
    'pipelinejob_states': table_pipelinejob_states(),
    'pipelinejob_events': table_pipelinejob_events(),
    'typeduuid_types': table_typeduuid_types(),
    'current_views': table_views(),
    'schema_version': text_schema_version(),
    'jsonschema_version': text_jsonschema_version()
}

# -- Project information -----------------------------------------------------

project = 'SD2 Data Catalog'
copyright = '2018, Matt Vaughn, Niall Gaffney, Mark Weston'
author = 'Matt Vaughn, Niall Gaffney, Mark Weston'

# The short X.Y version
version = code_version
# The full version, including alpha/beta/rc tags
release = '{}#{}'.format(code_version, '.'.join(list(schema_version_tuple)))

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

# Napoleon configs
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_extra_path = ['../schemas']

# html_context = {
#     'css_files': ['_static/theme_overrides.css']
# }

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'SD2DataCatalogdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'SD2DataCatalog.tex', 'SD2 Data Catalog Documentation',
     'Matt Vaughn, Niall Gaffney, Mark Weston', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'sd2datacatalog', 'SD2 Data Catalog Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'SD2DataCatalog', 'SD2 Data Catalog Documentation',
     author, 'SD2DataCatalog', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

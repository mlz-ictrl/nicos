# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('..')) # for custom extensions

import nicos

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
              'ext.setupdoc', 'ext.daemondoc', 'ext.tacostubs', 'ext.devicedoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
default_role = 'obj'

project = u'NICOS'
copyright = u'2009-2016, FRM II / NICOS contributors'  # pylint: disable=W0622
version = nicos.nicos_version
release = nicos.nicos_version

pygments_style = 'emacs'

html_title = 'NICOS documentation'
html_show_sourcelink = False
html_last_updated_fmt = '%F %H:%M'

_dark  = '#0b2c47'
_light = '#175791'

html_theme = 'default'

html_theme_options = {'sidebarbgcolor': '#EDF1F3',
                      'relbarbgcolor': '#DBDEDE',
                      'relbartextcolor': 'black',
                      'relbarlinkcolor': _dark,
                      'bgcolor': 'white',
                      'footerbgcolor': 'white',
                      'bodyfont': 'Arial, sans-serif',
                      'headfont': 'Arial, sans-serif',
                      'headbgcolor': 'white',
                      'headtextcolor': _dark,
                      'headlinkcolor': 'white',
                      'linkcolor': _light,
                      'visitedlinkcolor': _light,
                      'sidebartextcolor': 'black',
                      'sidebarlinkcolor': _dark,
                      'footertextcolor': 'black',
                      'stickysidebar': True,
                      'codebgcolor': '#F5F7F6',
                      }
html_static_path = ['_static']
html_style = 'nicos.css'

latex_documents = [
  ('contentspdf', 'NICOS.tex', u'NICOS v2 Documentation',
   u'NICOS contributors', 'manual'),
]
pdf_documents = [
  ('contentspdf', 'NICOS', u'NICOS v2 Documentation',
   u'NICOS contributors', 'manual'),
]
# A comma-separated list of custom stylesheets. Example:
pdf_stylesheets = ['frm2.json', 'sphinx', 'kerning', 'friendly', 'a4']

# A list of folders to search for stylesheets. Example:
pdf_style_path = ['.', '_styles','source']
# Mode for literal blocks wider than the frame. Can be
# overflow, shrink or truncate
pdf_fit_mode = "shrink"
# verbosity level. 0 1 or 2
pdf_verbosity = 1
# Section level that forces a break page.
# For example: 1 means top-level sections start in a new page
# 0 means disabled
pdf_break_level = 2
# Enable experimental feature to split table cells. Use it
# if you get "DelayedTable too big" errors
pdf_splittables = True
# When a section starts in a new page, force it to be 'even', 'odd',
# or just use 'any'
pdf_breakside = 'any'

# Insert footnotes where they are defined instead of
# at the end.
pdf_inline_footnotes = True
# Set the default DPI for images
pdf_default_dpi = 300
man_pages = [
    ('index', 'nicos', u'NICOS v2 Documentation',
     [u'NICOS contributors'], 1)
]

autodoc_default_options = ['members']

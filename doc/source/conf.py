# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.abspath('../../lib'))

extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
add_module_names = False
default_role = 'obj'

project = u'NICOS-ng'
copyright = u'2011, NICOS-ng contributors'
version = '2.0a1'
release = '2.0a1'

html_theme_options = {'sidebarbgcolor': 'white',
                      'relbarbgcolor': '#ccc',
                      'relbartextcolor': 'black',
                      'relbarlinkcolor': '#355f7c',
                      'bgcolor': 'white',
                      'footerbgcolor': 'white',
                      'bodyfont': 'Arial, sans-serif',
                      'headfont': 'Arial, sans-serif',
                      'sidebartextcolor': 'black',
                      'sidebarlinkcolor': '#355f7c',
                      'footertextcolor': 'black',
                      }

latex_documents = [
  ('index', 'NICOS-ng.tex', u'NICOS-ng Documentation',
   u'NICOS-ng contributors', 'manual'),
]

man_pages = [
    ('index', 'nicos-ng', u'NICOS-ng Documentation',
     [u'NICOS-ng contributors'], 1)
]

from sphinx import addnodes
from sphinx.domains.python import PyClassmember

class PyParameter(PyClassmember):
    def handle_signature(self, sig, signode):
        if ':' not in sig:
            return PyClassmember.handle_signature(self, sig, signode)
        name, descr = sig.split(':')
        name = name.strip()
        fullname, prefix = PyClassmember.handle_signature(self, name, signode)
        descr = ' (' + descr.strip() + ')'
        signode += addnodes.desc_annotation(descr, descr)
        return fullname, prefix

def setup(app):
    app.add_directive_to_domain('py', 'parameter', PyParameter)

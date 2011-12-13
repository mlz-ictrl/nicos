# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.abspath('../../lib'))

extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
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

autodoc_default_options = ['members']

from sphinx import addnodes
from nicos.utils import listof
from nicos.device import Device
from sphinx.domains import ObjType
from sphinx.domains.python import PyClassmember, PyModulelevel, PythonDomain
from sphinx.ext.autodoc import ClassDocumenter

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

orig_handle_signature = PyModulelevel.handle_signature
def new_handle_signature(self, sig, signode):
    ret = orig_handle_signature(self, sig, signode)
    for node in signode.children[:]:
        if node.tagname == 'desc_addname' and \
            node.astext().startswith('nicos.commands.'):
            signode.remove(node)
    return ret
PyModulelevel.handle_signature = new_handle_signature


class DeviceDocumenter(ClassDocumenter):
    priority = 20

    def add_directive_header(self, sig):
        ClassDocumenter.add_directive_header(self, sig)

        # add inheritance info, if wanted
        if not self.doc_as_attr:
            self.add_line(u'', '<autodoc>')
            if len(self.object.__bases__):
                bases = [b.__module__ == '__builtin__' and
                         u':class:`%s`' % b.__name__ or
                         u':class:`~%s.%s`' % (b.__module__, b.__name__)
                         for b in self.object.__bases__]
                self.add_line('   Bases: %s' % ', '.join(bases),
                              '<autodoc>')

    def document_members(self, all_members=False):
        if not issubclass(self.object, Device):
            return ClassDocumenter.document_members(self, all_members)
        if self.doc_as_attr:
            return
        self.add_line('.. rubric:: Parameters', '<autodoc>')
        self.add_line('', '<autodoc>')
        orig_indent = self.indent
        baseparams = {}
        for base in self.object.__bases__:
            baseparams.update(base.parameters)
        baseparaminfo = []
        n = 0
        for param, info in sorted(self.object.parameters.iteritems()):
            if param in baseparams:
                baseparaminfo.append((param, info))
                continue
            if isinstance(info.type, type(listof)):
                ptype = info.type.__doc__ or '?'
            else:
                ptype = info.type.__name__
            addinfo = []
            if info.settable: addinfo.append('settable at runtime')
            if info.mandatory: addinfo.append('mandatory in setup')
            if info.volatile: addinfo.append('volatile')
            if info.preinit: addinfo.append('initialized for preinit')
            if not info.userparam: addinfo.append('not shown to user')
            self.add_line('.. parameter:: %s : %s, %s' %
                          (param, ptype, ', '.join(addinfo)), '<autodoc>')
            self.add_line('', '<autodoc>')
            self.indent += self.content_indent
            descr = info.description or ''
            if descr and not descr.endswith('.'): descr += '.'
            self.add_line(descr, '<%s.%s description>' % (self.object, param))
            self.add_line('', '<autodoc>')
            self.add_line('Default value: ``' + repr(info.default) + '``',
                          '<autodoc>')
            self.add_line('', '<autodoc>')
            self.indent = orig_indent
            n += 1
        if n == 0:
            self.add_line('None defined.', '<autodoc>')
            self.add_line('', '<autodoc>')
        if baseparaminfo:
            self.add_line('Parameters inherited from the base classes: ' + ', '.join(
                '`.%s`' % name for (name, info) in baseparaminfo), '<autodoc>')

def setup(app):
    app.add_directive_to_domain('py', 'parameter', PyParameter)
    app.add_autodocumenter(DeviceDocumenter)
    PythonDomain.object_types['parameter'] = ObjType('parameter', 'attr', 'obj')

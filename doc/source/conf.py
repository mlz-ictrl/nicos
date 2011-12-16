# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.abspath('../../lib'))

extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
default_role = 'obj'

project = u'NICOS'
copyright = u'2011, FRM-II / NICOS contributors'
version = '2.0'
release = '2.0a1'

pygments_style = 'emacs'

html_title = 'NICOS documentation'
html_show_sourcelink = False
html_theme_options = {'sidebarbgcolor': '#EDF1F3',
                      'relbarbgcolor': '#DBDEDE',
                      'relbartextcolor': 'black',
                      'relbarlinkcolor': '#004682',
                      'bgcolor': 'white',
                      'footerbgcolor': 'white',
                      'bodyfont': 'Arial, sans-serif',
                      'headfont': 'Arial, sans-serif',
                      'headbgcolor': 'white',
                      'headtextcolor': '#004682',
                      'headlinkcolor': 'white',
                      'linkcolor': '#0072BD',
                      'visitedlinkcolor': '#0072BD',
                      'sidebartextcolor': 'black',
                      'sidebarlinkcolor': '#0072BD',
                      'footertextcolor': 'black',
                      'stickysidebar': True,
                      'codebgcolor': '#F5F7F6',
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
                         for b in self.object.__bases__ if b is not object]
                if bases:
                    self.add_line('   Bases: %s' % ', '.join(bases),
                                  '<autodoc>')

    def document_members(self, all_members=False):
        if not issubclass(self.object, Device) and not \
            hasattr(self.object, 'parameters'):
            return ClassDocumenter.document_members(self, all_members)
        if self.doc_as_attr:
            return
        orig_indent = self.indent
        myclsname = self.object.__module__ + '.' + self.object.__name__
        basecmdinfo = []
        if hasattr(self.object, 'commands'):
            n = 0
            for name, (args, doc) in sorted(self.object.commands.iteritems()):
                func = getattr(self.object, name)
                funccls = func.__module__ + '.' + func.im_class.__name__
                if funccls != myclsname:
                    basecmdinfo.append((funccls, name))
                    continue
                if n == 0:
                    self.add_line('**User methods**', '<autodoc>')
                    self.add_line('', '<autodoc>')
                self.add_line('.. method:: %s%s' % (name, args), '<autodoc>')
                self.add_line('', '<autodoc>')
                self.indent += self.content_indent
                for line in doc.splitlines():
                    self.add_line(line, '<doc of %s.%s>' % (self.object, name))
                self.add_line('', '<autodoc>')
                self.indent = orig_indent
                n += 1
            if basecmdinfo:
                self.add_line('Methods inherited from the base classes: ' +
                              ', '.join('`~%s.%s`' % i for i in basecmdinfo),
                              '<autodoc>')
        if getattr(self.object, 'attached_devices', None):
            self.add_line('**Attached devices**', '<autodoc>')
            self.add_line('', '<autodoc>')
            for adev, (cls, doc) in sorted(
                    self.object.attached_devices.iteritems()):
                if isinstance(cls, list):
                    atype = 'a list of `~%s.%s`' % (cls[0].__module__,
                                                    cls[0].__name__)
                else:
                    atype = '`~%s.%s`' % (cls.__module__, cls.__name__)
                descr = doc + (not doc.endswith('.') and '.' or '')
                self.add_line('.. parameter:: %s' % adev, '<autodoc>')
                self.add_line('', '<autodoc>')
                self.add_line('   %s Type: %s.' %  (descr, atype), '<autodoc>')
            self.add_line('', '<autodoc>')
        baseparaminfo = []
        n = 0
        for param, info in sorted(self.object.parameters.iteritems()):
            if info.classname != myclsname:
                baseparaminfo.append((param, info))
                continue
            if n == 0:
                self.add_line('**Parameters**', '<autodoc>')
                self.add_line('', '<autodoc>')
            if isinstance(info.type, type(listof)):
                ptype = info.type.__doc__ or '?'
            else:
                ptype = info.type.__name__
            addinfo = [ptype]
            if info.settable: addinfo.append('settable at runtime')
            if info.mandatory: addinfo.append('mandatory in setup')
            if info.volatile: addinfo.append('volatile')
            if info.preinit: addinfo.append('initialized for preinit')
            if not info.userparam: addinfo.append('not shown to user')
            self.add_line('.. parameter:: %s : %s' %
                          (param, ', '.join(addinfo)), '<autodoc>')
            self.add_line('', '<autodoc>')
            self.indent += self.content_indent
            descr = info.description or ''
            if descr and not descr.endswith('.'): descr += '.'
            if not info.mandatory:
                descr += ' Default value: ``%r``.' % (info.default,)
            if info.unit:
                if info.unit == 'main':
                    descr += ' Unit: same as device value.'
                else:
                    descr += ' Unit: ``%s``.' % info.unit
            self.add_line(descr, '<%s.%s description>' % (self.object, param))
            self.add_line('', '<autodoc>')
            self.indent = orig_indent
            n += 1
        if baseparaminfo:
            self.add_line('Parameters inherited from the base classes: ' +
                          ', '.join('`~%s.%s`' % (info.classname or '', name)
                          for (name, info) in baseparaminfo), '<autodoc>')

def setup(app):
    app.add_directive_to_domain('py', 'parameter', PyParameter)
    app.add_autodocumenter(DeviceDocumenter)
    PythonDomain.object_types['parameter'] = ObjType('parameter', 'attr', 'obj')

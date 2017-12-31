#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""Support for better documenting NICOS device classes:

* handle parameters like attributes, but with an annotation of their type
* automatically document attached devices
* automatically document all the parameters of a class and refer to the ones
  inherited by base classes
"""

import inspect

from docutils import nodes
from sphinx import addnodes
from sphinx.domains import ObjType
from sphinx.domains.python import PyClassmember, PyModulelevel, PythonDomain
from sphinx.ext.autodoc import ClassDocumenter

from nicos.core import Device
from nicos.core.mixins import DeviceMixinBase
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.pycompat import getargspec


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


class PyDerivedParameter(PyClassmember):
    def handle_signature(self, sig, signode):
        if ':' not in sig:
            return PyClassmember.handle_signature(self, sig, signode)
        fullname, descr = sig.split(':')
        fullname = fullname.strip()
        clsname, name = fullname.rsplit('.', 1)
        namenode = addnodes.desc_name('', '')
        refnode = addnodes.pending_xref('', refdomain='py', reftype='attr',
                                        reftarget=name)
        refnode['py:class'] = clsname
        refnode += nodes.Text(name, name)
        namenode += refnode
        signode += namenode
        descr = ' (' + descr.strip() + ')'
        signode += addnodes.desc_annotation(descr, descr)
        return fullname, clsname + '.'

    def add_target_and_index(self, name_cls, sig, signode):
        pass


orig_handle_signature = PyModulelevel.handle_signature


def new_handle_signature(self, sig, signode):
    ret = orig_handle_signature(self, sig, signode)
    for node in signode.children[:]:
        if node.tagname == 'desc_addname' and \
           node.astext().startswith('nicos.commands.'):
            signode.remove(node)
    return ret
PyModulelevel.handle_signature = new_handle_signature


class NicosClassDocumenter(ClassDocumenter):
    priority = 20

    def add_directive_header(self, sig):
        ClassDocumenter.add_directive_header(self, sig)

        # add inheritance info, if wanted
        if not self.doc_as_attr:
            self.add_line(u'', '<autodoc>')
            if self.object.__bases__:
                bases = [b.__module__ == '__builtin__' and
                         u':class:`%s`' % b.__name__ or
                         u':class:`~%s.%s`' % (b.__module__, b.__name__)
                         for b in self.object.__bases__ if b is not object]
                if bases:
                    self.add_line('   Bases: %s' % ', '.join(bases),
                                  '<autodoc>')

    def _format_methods(self, methodlist, orig_indent):
        myclsname = self.object.__module__ + '.' + self.object.__name__
        basecmdinfo = []
        n = 0
        for name, (args, doc, funccls, is_usermethod) in sorted(methodlist):
            if not is_usermethod:
                continue
            func = getattr(self.object, name)
            funccls = func.__module__ + '.' + funccls.__name__
            if funccls != myclsname:
                basecmdinfo.append((funccls, name))
                continue
            if n == 0:
                self.add_line('**User methods**', '<autodoc>')
                self.add_line('', '<autodoc>')
            self.add_line('.. method:: %s%s' % (name, args), '<autodoc>')
            self.add_line('', '<autodoc>')
            self.indent += self.content_indent
            if not doc:
                self.env.app.warn('%s.%s: usermethod has no documentation' %
                                  (myclsname, name))
            for line in doc.splitlines():
                self.add_line(line, '<doc of %s.%s>' % (self.object, name))
            self.add_line('', '<autodoc>')
            self.indent = orig_indent
            n += 1
        if basecmdinfo:
            self.add_line('', '<autodoc>')
            self.add_line('Methods inherited from the base classes: ' +
                          ', '.join('`~%s.%s`' % i for i in basecmdinfo),
                          '<autodoc>')
            self.add_line('', '<autodoc>')

    def _format_attached_devices(self, attachedlist):
        self.add_line('**Attached devices**', '<autodoc>')
        self.add_line('', '<autodoc>')
        for adev, attach in sorted(attachedlist):
            if (isinstance(attach.multiple, list) and attach.multiple[0] > 1) \
               or isinstance(attach.multiple, bool):
                n = ''
                if isinstance(attach.multiple, list):
                    if len(attach.multiple) > 1:
                        n = '%d to %d ' % attach.multiple
                    else:
                        n = '%d ' % attach.multiple[0]
                atype = 'a list of %s`~%s.%s`' % (
                    n, attach.devclass.__module__,
                    attach.devclass.__name__)
            else:
                atype = '`~%s.%s`' % (attach.devclass.__module__,
                                      attach.devclass.__name__)
            if attach.optional:
                atype += ' (optional)'
            descr = attach.description + \
                (not attach.description.endswith('.') and '.' or '')
            self.add_line('.. parameter:: %s' % adev, '<autodoc>')
            self.add_line('', '<autodoc>')
            self.add_line('   %s Type: %s.' % (descr, atype), '<autodoc>')
        self.add_line('', '<autodoc>')

    def document_members(self, all_members=False):
        if not issubclass(self.object, Device) and \
           not issubclass(self.object, DeviceMixinBase) and \
           not issubclass(self.object, NicosWidget):
            return ClassDocumenter.document_members(self, all_members)

        if self.doc_as_attr:
            return
        orig_indent = self.indent

        if issubclass(self.object, NicosWidget):
            self._format_properties(self.object, orig_indent)

        if hasattr(self.object, 'methods'):
            self._format_methods(self.object.methods.items(), orig_indent)

        if getattr(self.object, 'attached_devices', None):
            self._format_attached_devices(self.object.attached_devices.items())

        if not hasattr(self.object, 'parameters'):
            return

        mandatoryparaminfo = []
        optionalparaminfo = []
        baseparaminfo = []

        myclsname = self.object.__module__ + '.' + self.object.__name__
        for param, info in sorted(self.object.parameters.items()):
            if not info.userparam:
                continue
            if info.classname is not None and info.classname != myclsname:
                baseparaminfo.append((param, info))
                info.derived = True
            else:
                info.derived = False
            if info.mandatory:
                mandatoryparaminfo.append((param, info))
            else:
                optionalparaminfo.append((param, info))

        if mandatoryparaminfo or optionalparaminfo:
            self.add_line('', '<autodoc>')
            self.add_line('**Parameters**', '<autodoc>')
            self.add_line('', '<autodoc>')

        if mandatoryparaminfo:
            self.add_line('', '<autodoc>')
            self.add_line('*Mandatory*', '<autodoc>')
            self.add_line('', '<autodoc>')
            self._format_parameters(mandatoryparaminfo, orig_indent)

        if optionalparaminfo:
            self.add_line('', '<autodoc>')
            self.add_line('*Optional*', '<autodoc>')
            self.add_line('', '<autodoc>')
            self._format_parameters(optionalparaminfo, orig_indent)

        if baseparaminfo:
            self.add_line('', '<autodoc>')
            self.add_line('Parameters inherited from the base classes are: ' +
                          ', '.join('`~%s.%s`' % (info.classname or '', name)
                                    for (name, info) in baseparaminfo),
                          '<autodoc>')

    def _format_properties(self, obj, orig_indent):
        self.add_line('', '<autodoc>')
        self.add_line('**Parameters**', '<autodoc>')
        self.add_line('', '<autodoc>')

        for prop in sorted(dir(obj.__class__)):
            info = getattr(obj.__class__, prop, None)
            if not isinstance(info, PropDef):
                continue
            if isinstance(info.ptype, type):
                ptype = info.ptype.__name__
            else:
                ptype = info.ptype or '?'
            addinfo = [ptype]  # info.doc info.ptype, info.default
            self.add_line('.. parameter:: %s : %s' %
                          (prop, ', '.join(addinfo)), '<autodoc>')
            self.add_line('', '<autodoc>')
            descr = info.doc or ''
            if descr and not descr.endswith(('.', '!', '?')):
                descr += '.'
            self.indent += self.content_indent
            self.add_line(descr, '<%s.%s description>' % (self.object, prop))
            # self.add_line('', '<autodoc>')
            self.indent = orig_indent

    def _format_parameters(self, paraminfolist, orig_indent):
        for (param, info) in paraminfolist:
            if isinstance(info.type, type):
                ptype = info.type.__name__
            else:
                ptype = info.type.__doc__ or '?'
            addinfo = [ptype]
            if info.settable:
                addinfo.append('settable at runtime')
            if info.volatile:
                addinfo.append('volatile')
            if info.derived:
                self.add_line('.. derivedparameter:: %s.%s : %s' %
                              (info.classname, param, ', '.join(addinfo)),
                              '<autodoc>')
            else:
                self.add_line('.. parameter:: %s : %s' %
                              (param, ', '.join(addinfo)), '<autodoc>')
            self.add_line('', '<autodoc>')
            self.indent += self.content_indent
            descr = info.description or ''
            if descr and not descr.endswith(('.', '!', '?')):
                descr += '.'
            descr = descr.decode('utf-8')
            if not info.mandatory:
                descr += ' Default value: ``%r``.' % (info.default,)
            if info.unit:
                if info.unit == 'main':
                    descr += ' Unit: same as device value.'
                else:
                    descr += ' Unit: ``%s``.' % info.unit
            self.add_line(descr, '<%s.%s description>' % (self.object, param))
            if info.ext_desc:
                self.add_line('', '<autodoc>')
                for line in info.ext_desc.splitlines():
                    self.add_line(line.rstrip(), '<%s.%s>' % (self.object, param))
            self.add_line('', '<autodoc>')
            self.indent = orig_indent


def process_signature(app, objtype, fullname, obj, options, args, retann):
    # for user commands, fix the signature:
    # a) use original function for functions wrapped by decorators
    # b) use designated "helparglist" for functions that have it
    if objtype == 'function' and fullname.startswith('nicos.commands.'):
        while hasattr(obj, 'real_func'):
            obj = obj.real_func
        if hasattr(obj, 'help_arglist'):
            return '(' + obj.help_arglist + ')', retann
        else:
            return inspect.formatargspec(*getargspec(obj)), retann


def setup(app):
    app.add_directive_to_domain('py', 'parameter', PyParameter)
    app.add_directive_to_domain('py', 'derivedparameter', PyDerivedParameter)
    app.add_autodocumenter(NicosClassDocumenter)
    app.connect('autodoc-process-signature', process_signature)
    PythonDomain.object_types['parameter'] = ObjType('parameter', 'attr', 'obj')
    return {'parallel_read_safe': True,
            'version': '0.1.0', }

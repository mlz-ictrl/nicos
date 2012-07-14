#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Utilities to generate HTML-format help for displaying in the GUI client."""

__version__ = "$Revision$"

import sys
import pydoc
import inspect
import threading
from cgi import escape
from cStringIO import StringIO

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = None
else:
    # black magic to make `cmd` into links
    from docutils import nodes, utils
    from docutils.parsers.rst import roles
    def std_role(typ, raw, text, lineno, inliner, options={}, content=[]):
        text = utils.unescape(text)
        reftext = text
        if reftext.endswith('()'): reftext = reftext[:-2]
        return [nodes.reference(text, text, refuri='cmd:%s' % reftext)], []
    roles._roles[''] = std_role

from nicos import session
from nicos.core import Device
from nicos.utils import formatDocstring

STYLE = '''
body    { font-family: 'Helvetica', 'Arial', sans-serif;
          font-size: 12pt; }
pre, tt { font-family: 'Consolas', 'Dejavu Sans Mono', monotype;
          font-size: 11pt; }
a       { text-decoration: none; color: #03c; }
a:hover { text-decoration: underline; color: #05f; }
table   { border-collapse: collapse; }
td, th  { border: 1px solid #ccc; padding: 3px; }
th      { text-align: left; }
pre.literal-block
        { background-color: #eee; padding: 2px;
          border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; }
.menu   { text-align: right; }
.usage  { font-weight: bold; }
'''


class HelpGenerator(object):

    def __init__(self):
        self.header = '<style type="text/css">%s</style>' % STYLE
        self.footer = ''
        self.strio = StringIO()
        self.lock = threading.Lock()
        self.helper = pydoc.Helper(output=self.strio)
        self._specialtopics = set(self.helper.topics)
        self._specialtopics.update(self.helper.symbols)
        self._specialtopics.update(self.helper.keywords)

    def gen_heading(self, title, id=''):
        if id:
            id = ' id="%s"' % escape(id)
        return '<h3%s>%s</h3>' % (id, escape(title))

    def gen_markup(self, markup):
        if publish_parts is None:
            return '<pre>' + escape(markup) + '</pre>'
        else:
            try:
                return publish_parts(markup, writer_name='html')['fragment']
            except Exception, err:
                print err
                return '<pre>' + escape(markup) + '</pre>'

    def gen_helpindex(self):
        ret = ['<p class="menu">'
               '<a href="#commands">Commands</a>&nbsp;&nbsp;|&nbsp;&nbsp;'
               '<a href="#devices">Devices</a></p>']
        cmds = []
        for obj in session.getExportedObjects():
            if not hasattr(obj, 'is_usercommand'):
                continue
            real_func = getattr(obj, 'real_func', obj)
            if real_func.__name__.startswith('_'):
                continue
            if real_func.is_hidden:
                continue
            if hasattr(real_func, 'help_arglist'):
                argspec = '(%s)' % real_func.help_arglist
            else:
                argspec = inspect.formatargspec(*inspect.getargspec(real_func))
            signature = '<tt><a href="cmd:%s">%s</a>' % ((real_func.__name__,)*2) + \
                escape(argspec) + '</tt>'
            docstring = escape(real_func.__doc__ or ' ').splitlines()[0]
            cmds.append('<tr><td>%s</td><td>%s</td></tr>' %
                        (signature, docstring))
        cmds.sort()
        ret.append(self.gen_heading('NICOS commands', 'commands'))
        ret.append('<table width="100%">'
                   '<tr><th>Name</th><th>Description</th></tr>')
        ret.extend(cmds)
        ret.append('</table>')
        ret.append(self.gen_heading('Devices', 'devices'))
        ret.append('<table width="100%">'
                   '<tr><th>Name</th><th>Type</th><th>Description</th></tr>')
        for devname in sorted(session.explicit_devices):
            dev = session.devices[devname]
            ret.append('<tr><td><tt><a href="dev:%s">%s</a></tt></td>'
                       '<td>%s</td><td>%s</td>' %
                       (dev, dev, dev.__class__.__name__, escape(dev.description)))
        ret.append('</table>')
        return ''.join(ret)

    def gen_funchelp(self, func):
        ret = []
        real_func = getattr(func, 'real_func', func)
        if hasattr(real_func, 'help_arglist'):
            argspec = '(%s)' % real_func.help_arglist
        else:
            argspec = inspect.formatargspec(*inspect.getargspec(real_func))
        ret.append(self.gen_heading('Help on %s command' % real_func.__name__))
        ret.append('<p class="usage">Usage: <tt>' +
                   escape(real_func.__name__ + argspec) +
                   '</tt></p>')
        docstring = '\n'.join(formatDocstring(real_func.__doc__ or ''))
        ret.append(self.gen_markup(docstring))
        return ''.join(ret)

    def gen_devhelp(self, dev):
        ret = []
        ret.append(self.gen_heading('Help on %s device' % dev))
        ret.append('<p class="devcls">%s is a device of class %s.</p>' %
                   (dev.name, dev.__class__.__name__))
        if dev.description:
            ret.append('<p class="devdesc">Device description: ' +
                       escape(dev.description) + '</p>')
        if dev.__class__.__doc__:
            clsdoc = '\n'.join(formatDocstring(dev.__class__.__doc__))
            ret.append('<p class="clsdesc">Device class description:</p>' +
                       '<blockquote>' + self.gen_markup(clsdoc) + '</blockquote>')
        ret.append('<h4>Device methods</h4>')
        ret.append('<table width="100%"><tr><th>Method</th><th>From class</th>'
                   '<th>Description</th></tr>')
        listed = set()
        def _list(cls):
            if cls in listed: return
            listed.add(cls)
            for name, (args, doc) in sorted(cls.commands.iteritems()):
                ret.append('<tr><td><tt>%s</tt></td><td>%s</td><td>%s</td></tr>' %
                           (escape(dev.name + '.' + name + args), cls.__name__,
                            escape(doc)))
            for base in cls.__bases__:
                if issubclass(base, Device):
                    _list(base)
        _list(dev.__class__)
        ret.append('</table>')
        ret.append('<h4>Device parameters</h4>')
        ret.append('<table width="100%"><tr><th>Name</th><th>Current value</th>'
                   '<th>Unit</th><th>Settable?</th><th>Description</th></tr>')
        devunit = getattr(dev, 'unit', '')
        for name, info in sorted(dev.parameters.iteritems()):
            if not info.userparam:
                continue
            try:
                value = getattr(dev, name)
            except Exception:
                value = '<could not get value>'
            unit = (info.unit or '').replace('main', devunit)
            vstr = repr(value)
            if len(vstr) > 50:
                vstr = vstr[:47] + '...'
            settable = info.settable and 'yes' or 'no'
            name = dev.name + '.' + name
            ret.append('<tr><td><tt>%s</tt></td><td>%s</td><td>%s</td>'
                       '<td>%s</td><td>%s</td></tr>' %
                       (name, escape(vstr), escape(unit), settable,
                        escape(info.description)))
        ret.append('</table>')
        return ''.join(ret)

    def gen_helptarget(self, target):
        if target == 'index':
            return self.gen_helpindex()
        elif target.startswith('cmd:'):
            cmdname = target[4:]
            obj = session.namespace[cmdname]
            return self.gen_funchelp(obj)
        elif target.startswith('dev:'):
            devname = target[4:]
            obj = session.namespace[devname]
            return self.gen_devhelp(obj)
        else:
            raise ValueError

    def gen_genericdoc(self, obj):
        # unfortunately the Helper does not output all into its assigned output
        # object, so we need to redirect sys.stdout as well...
        with self.lock:
            self.strio.truncate(0)
            old_stdout = sys.stdout
            sys.stdout = self.strio
            try:
                self.helper.help(obj)
            finally:
                sys.stdout = old_stdout
            ret = self.strio.getvalue()
        return '<pre>' + escape(ret) + '</pre>'

    def generate(self, obj):
        if obj is None:
            obj = 'index'
        if isinstance(obj, str) and obj not in self._specialtopics:
            return obj, self.header + self.gen_helptarget(obj) + self.footer
        elif isinstance(obj, Device):
            return 'dev:%s' % obj, \
                self.header + self.gen_devhelp(obj) + self.footer
        elif inspect.isfunction(obj):
            return 'cmd:%s' % obj.__name__, \
                self.header + self.gen_funchelp(obj) + self.footer
        else:
            return '', \
                self.header + self.gen_genericdoc(obj) + self.footer

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import sys
import pydoc
import inspect
import threading

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = None
else:
    # black magic to make `cmd` into links
    from docutils import nodes, utils
    from docutils.parsers.rst import roles

    def std_role(typ, raw, text, lineno, inliner, options=None, content=None):
        text = utils.unescape(text)
        reftext = text
        if reftext.endswith('()'):
            reftext = reftext[:-2]
        return [nodes.reference(text, text, refuri='cmd:%s' % reftext)], []
    roles._roles[''] = std_role

from nicos import session
from nicos.core import Device
from nicos.utils import formatDocstring
from nicos.pycompat import StringIO, escape_html, iteritems, string_types


STYLE = '''
body    { font-family: 'Helvetica', 'Arial', sans-serif;
          font-size: 12pt; line-height: 120%; }
pre, tt { font-family: 'Consolas', 'Dejavu Sans Mono', monotype;
          font-size: 11pt; }
a       { text-decoration: none; color: #03c; }
a:hover { text-decoration: underline; color: #05f; }
table   { border-collapse: collapse; }
td, th  { border: 1px solid #ccc; padding: 3px; }
th      { text-align: left; }
pre.literal-block, pre.doctest-block
        { background-color: #efe; padding: 3px;
          border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; }
.menu   { text-align: right; }
.usage, .devdesc
        { font-weight: bold; padding: 3px 0; background-color: #eef;
          border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; }
.usage tt
        { font-size: 13pt; }
'''


def lower(s):
    return s.lower()


class HelpGenerator(object):

    def __init__(self):
        self.header = ('<html><head><style type="text/css">%s</style>'
                       '</head>\n<body>' % STYLE)
        self.footer = '</body></html>'
        self.strin = StringIO()
        self.strout = StringIO()
        self.lock = threading.Lock()
        self.helper = pydoc.Helper(input=self.strin, output=self.strout)
        self._specialtopics = set(self.helper.topics)
        if hasattr(self.helper, 'symbols'):
            self._specialtopics.update(self.helper.symbols)
        self._specialtopics.update(self.helper.keywords)

    def gen_heading(self, title, id_=''):
        if id_:
            id_ = ' id="%s"' % escape_html(id_)
        return '<h3%s>%s</h3>' % (id_, escape_html(title))

    def gen_markup(self, markup):
        if publish_parts is None:
            return '<pre>' + escape_html(markup) + '</pre>'
        else:
            try:
                return publish_parts(markup, writer_name='html')['fragment']
            except Exception:
                return '<pre>' + escape_html(markup) + '</pre>'

    def gen_helpindex(self):
        ret = ['<p class="menu">'
               '<a href="#commands">Commands</a>&nbsp;&nbsp;|&nbsp;&nbsp;'
               '<a href="#devices">Devices</a>&nbsp;&nbsp;|&nbsp;&nbsp;'
               '<a href="#setups">Setups</a></p>']
        ret.append('<p>Welcome to the NICOS interactive help!</p>')
        cmds = []
        for name, obj in session.getExportedObjects():
            if not hasattr(obj, 'is_usercommand'):
                continue
            real_func = getattr(obj, 'real_func', obj)
            if real_func.__name__.startswith('_'):
                continue
            if getattr(real_func, 'is_hidden', False):
                continue
            if real_func.__name__ != name:
                # it's an alias, don't show it again
                continue
            if hasattr(real_func, 'help_arglist'):
                argspec = '(%s)' % real_func.help_arglist
            else:
                argspec = inspect.formatargspec(*inspect.getargspec(real_func))
            signature = '<tt><a href="cmd:%s">%s</a></tt><small>' % \
                ((real_func.__name__,)*2) + escape_html(argspec) + '</small>'
            docstring = escape_html(real_func.__doc__ or ' ').splitlines()[0]
            cmds.append('<tr><td>%s</td><td>%s</td></tr>' %
                        (signature, docstring))
        cmds.sort()
        ret.append(self.gen_heading('NICOS commands', 'commands'))
        ret.append('<p>These commands are currently available.</p>')
        ret.append('<table width="100%">'
                   '<tr><th>Name</th><th>Short description</th></tr>')
        ret.extend(cmds)
        ret.append('</table>')
        ret.append(self.gen_heading('Devices', 'devices'))
        ret.append('<p>These are the currently loaded high-level devices.  Use '
                   '<a href="cmd:AddSetup">AddSetup()</a> or the "Setup" '
                   'window to add more devices.</p>')
        ret.append('<table width="100%"><tr><th>Name</th><th>Type</th>'
                   '<th>From setup</th><th>Description</th></tr>')
        setupinfo = session.getSetupInfo()
        devsetups = {}
        for sname, info in iteritems(setupinfo):
            if info is None:
                continue
            for devname in info['devices']:
                devsetups[devname] = sname
        for devname in sorted(session.explicit_devices, key=lower):
            dev = session.devices[devname]
            ret.append('<tr><td><tt><a href="dev:%s">%s</a></tt></td>'
                       '<td>%s</td><td>%s</td><td>%s</td>' %
                       (dev, dev, dev.__class__.__name__,
                        devsetups.get(devname, ''), escape_html(dev.description)))
        ret.append('</table>')
        ret.append(self.gen_heading('Setups', 'setups'))
        ret.append('<p>These are the available setups.  Use '
                   '<a href="cmd:AddSetup">AddSetup()</a> to load an '
                   'additional setup or <a href="cmd:NewSetup">NewSetup()</a>'
                   ' to load one or more completely new ones.</p>')

        def devlink(devname):
            if devname in session.devices:
                return '<a href="dev:%s">%s</a>' % (escape_html(devname),
                                                    escape_html(devname))
            return escape_html(devname)

        def listsetups(group):
            setups = []
            for setupname, info in sorted(iteritems(session.getSetupInfo())):
                if info is None or info['group'] != group:
                    continue
                setups.append('<tr><td><tt>%s</tt></td><td>%s</td>'
                              '<td>%s</td><td>%s</td></tr>' %
                              (setupname,
                               setupname in session.loaded_setups and 'yes' or '',
                               escape_html(info['description']),
                               ', '.join(map(devlink,
                                             sorted(info['devices'], key=lower)))))
            ret.append('<table width="100%"><tr><th>Name</th><th>Loaded</th>'
                       '<th>Description</th><th>Devices</th></tr>')
            ret.extend(setups)
            ret.append('</table>')
        ret.append('<h4>Basic instrument setups</h4>')
        listsetups('basic')
        ret.append('<h4>Optional setups</h4>')
        listsetups('optional')
        ret.append('<h4>Plug-and-play setups</h4>')
        listsetups('plugplay')
        return ''.join(ret)

    def gen_funchelp(self, func):
        ret = []
        real_func = getattr(func, 'real_func', func)
        if hasattr(real_func, 'help_arglist'):
            argspec = '(%s)' % real_func.help_arglist
        else:
            argspec = inspect.formatargspec(*inspect.getargspec(real_func))
        ret.append(self.gen_heading('Help on the %s command' % real_func.__name__))
        ret.append('<p class="usage">Usage: <tt>' +
                   escape_html(real_func.__name__ + argspec) +
                   '</tt></p>')
        docstring = '\n'.join(formatDocstring(real_func.__doc__ or ''))
        ret.append(self.gen_markup(docstring))
        return ''.join(ret)

    def gen_devhelp(self, dev):
        ret = []
        ret.append(self.gen_heading('Help on the %s device' % dev))
        ret.append('<p class="devcls">%s is a device of class %s.</p>' %
                   (dev.name, dev.__class__.__name__))
        if dev.description:
            ret.append('<p class="devdesc">Device description: ' +
                       escape_html(dev.description) + '</p>')
        if dev.__class__.__doc__:
            clsdoc = '\n'.join(formatDocstring(dev.__class__.__doc__))
            ret.append('<p class="clsdesc">Device class description:</p>' +
                       '<blockquote>' + self.gen_markup(clsdoc) + '</blockquote>')
        ret.append('<h4>Device parameters</h4>')
        ret.append('<table width="100%"><tr><th>Name</th><th>Current value</th>'
                   '<th>Unit</th><th>Settable?</th><th>Value type</th>'
                   '<th>Description</th></tr>')
        devunit = getattr(dev, 'unit', '')
        for name, info in sorted(iteritems(dev.parameters)):
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
            if isinstance(info.type, type):
                ptype = info.type.__name__
            else:
                ptype = info.type.__doc__ or '?'
            ret.append('<tr><td><tt>%s</tt></td><td>%s</td><td>%s</td>'
                       '<td>%s</td><td>%s</td><td>%s</td></tr>' %
                       (name, escape_html(vstr), escape_html(unit), settable,
                        escape_html(ptype), escape_html(info.description)))
        ret.append('</table>')
        ret.append('<h4>Device methods</h4>')
        ret.append('<table width="100%"><tr><th>Method</th><th>From class</th>'
                   '<th>Description</th></tr>')
        listed = set()

        def _list(cls):
            if cls in listed:
                return
            listed.add(cls)
            for name, (args, doc) in sorted(iteritems(cls.commands)):
                ret.append('<tr><td><tt>%s</tt></td><td>%s</td><td>%s</td></tr>' %
                           (escape_html(dev.name + '.' + name + args), cls.__name__,
                            escape_html(doc)))
            for base in cls.__bases__:
                if issubclass(base, Device):
                    _list(base)
        _list(dev.__class__)
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
            self.strout.truncate(0)
            old_stdout = sys.stdout
            sys.stdout = self.strout
            try:
                self.helper.help(obj)
            finally:
                sys.stdout = old_stdout
            ret = self.strout.getvalue()
        return self.gen_heading('Python help on %r' % obj) + \
            '<pre>' + escape_html(ret) + '</pre>'

    def generate(self, obj):
        if obj is None:
            obj = 'index'
        if isinstance(obj, string_types) and obj not in self._specialtopics:
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

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Utilities to generate HTML-format help for displaying in the GUI client."""

import html
import inspect
import pydoc
import sys
import threading
from io import StringIO

from nicos import session
from nicos.core import Device, DeviceAlias
from nicos.utils import formatArgs, formatDocstring

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = std_role = None
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



STYLE = """
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
.devalias
        { font-weight: bold; padding: 3px 0; background-color: #fee;
          border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; }
.usage, .devdesc
        { font-weight: bold; padding: 3px 0; background-color: #eef;
          border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; }
.usage tt
        { font-size: 13pt; }
"""


def lower(s):
    return s.lower()


class HelpGenerator:

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
            id_ = ' id="%s"' % html.escape(id_)
        return '<h3%s>%s</h3>' % (id_, html.escape(title))

    def gen_markup(self, markup):
        if publish_parts is None:
            return '<pre>' + html.escape(markup) + '</pre>'
        roles.register_local_role('', std_role)
        try:
            return publish_parts(markup, writer_name='html')['html_body']
        except Exception:
            return '<pre>' + html.escape(markup) + '</pre>'

    def gen_helpindex(self):
        ret = ['<p class="menu">'
               '<a href="#commands">Commands</a>&nbsp;&nbsp;|&nbsp;&nbsp;'
               '<a href="#devices">Devices</a>&nbsp;&nbsp;|&nbsp;&nbsp;'
               '<a href="#setups">Setups</a></p>']
        ret.append('<p>Welcome to the NICOS interactive help!</p>')

        if session.help_topics:
            ret.append(self.gen_heading('List of additional help topics for '
                                        'currently loaded setup', 'help_topics'))
            for topic in sorted(session.help_topics):
                ret.append('<h4><a href="topic:%s">%s</a></h4>' % (topic, topic))

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
                argspec = formatArgs(real_func)
            signature = '<tt><a href="cmd:%s">%s</a></tt><small>' % \
                ((real_func.__name__,)*2) + html.escape(argspec) + '</small>'
            docstring = html.escape(real_func.__doc__ or ' ').splitlines()[0]
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
        for sname, info in setupinfo.items():
            if info is None:
                continue
            for devname in info['devices']:
                devsetups[devname] = sname
        for devname in sorted(session.explicit_devices, key=lower):
            dev = session.devices[devname]
            ret.append('<tr><td><tt><a href="dev:%s">%s</a></tt></td>'
                       '<td>%s</td><td>%s</td><td>%s</td>' %
                       (dev, dev, dev.__class__.__name__,
                        devsetups.get(devname, ''), html.escape(dev.description)))
        ret.append('</table>')
        ret.append(self.gen_heading('Setups', 'setups'))
        ret.append('<p>These are the available setups.  Use '
                   '<a href="cmd:AddSetup">AddSetup()</a> to load an '
                   'additional setup or <a href="cmd:NewSetup">NewSetup()</a>'
                   ' to load one or more completely new ones.</p>')

        def devlink(devname):
            if devname in session.devices:
                return '<a href="dev:%s">%s</a>' % (html.escape(devname),
                                                    html.escape(devname))
            return html.escape(devname)

        def listsetups(group):
            setups = []
            for setupname, info in sorted(session.getSetupInfo().items()):
                if info is None or info['group'] != group:
                    continue
                setups.append('<tr><td><tt>%s</tt></td><td>%s</td>'
                              '<td>%s</td><td>%s</td></tr>' %
                              (setupname,
                               setupname in session.loaded_setups and 'yes' or '',
                               html.escape(info['description']),
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
            argspec = formatArgs(real_func)
        ret.append(self.gen_heading('Help on the %s command' %
                                    real_func.__name__))
        ret.append('<p class="usage">Usage: <tt>' +
                   html.escape(real_func.__name__ + argspec) +
                   '</tt></p>')
        docstring = '\n'.join(formatDocstring(real_func.__doc__ or ''))
        ret.append(self.gen_markup(docstring))
        return ''.join(ret)

    def gen_methodhelp(self, func, dev=''):
        ret = []
        if hasattr(func, 'help_arglist'):
            argspec = '(%s)' % func.help_arglist
        else:
            argspec = formatArgs(func)
        ret.append(self.gen_heading(f'Help on the {dev}.{func.__name__} '
                                    'user method'))
        ret.append('<p class="usage">Usage: <tt>' +
                   html.escape(dev + '.' + func.__name__ + argspec) +
                   '</tt></p>')
        docstring = getattr(func, 'help_doc', func.__doc__ or '')
        docstring = '\n'.join(formatDocstring(docstring))
        ret.append(self.gen_markup(docstring))
        return ''.join(ret)

    def gen_devhelp(self, dev):
        ret = []
        ret.append(self.gen_heading('Help on the %s device' % dev))
        ret.append('<p class="devcls">%s is a device of class %s.</p>' %
                   (dev.name, dev.__class__.__name__))
        if isinstance(dev, DeviceAlias):
            points = dev.alias
            if points:
                ret.append('<p class="devalias">%s is a device alias, it '
                           'points to <a href="dev:%s">%s</a>.' % (
                               dev, points, points))
            else:
                ret.append('<p class="devalias">%s is a device alias, it '
                           'points to nothing at the moment.')
        if dev.description:
            ret.append('<p class="devdesc">Device description: ' +
                       html.escape(dev.description) + '</p>')
        if dev.__class__.__doc__:
            clsdoc = '\n'.join(formatDocstring(dev.__class__.__doc__))
            ret.append('<p class="clsdesc">Device class description:</p>' +
                       '<blockquote>' + self.gen_markup(clsdoc) + '</blockquote>')
        ret.append('<h4>Device parameters</h4>')
        ret.append('<table width="100%"><tr><th>Name</th><th>Current value</th>'
                   '<th>Unit</th><th>Settable?</th><th>Value type</th>'
                   '<th>Description</th></tr>')
        devunit = getattr(dev, 'unit', '')
        for name, info in sorted(dev.parameters.items()):
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
            ext_desc = ''
            if info.ext_desc:
                ext_desc = f'<br>{html.escape(info.ext_desc)}'
            ret.append('<tr><td><tt>%s</tt></td><td>%s</td><td>%s</td>'
                       '<td>%s</td><td>%s</td><td>%s</td></tr>' %
                       (name, html.escape(vstr), html.escape(unit), settable,
                        html.escape(ptype), html.escape(info.description) +
                        ext_desc))
        ret.append('</table>')
        ret.append('<h4>Device methods</h4>')
        ret.append('<table width="100%"><tr><th>Method</th><th>From class</th>'
                   '<th>Description</th></tr>')
        listed = set()

        def _list(cls):
            if cls in listed:
                return
            listed.add(cls)
            for name, (args, doc, fromtype, is_usermethod) in sorted(cls.methods.items()):
                if is_usermethod and fromtype is cls:
                    ret.append('<tr><td><tt><a href="method:%s">%s</a></tt></td><td>%s</td><td>%s</td></tr>' %
                               (dev.name + '.' + name,
                                dev.name + '.' + name + html.escape(args),
                                cls.__name__, html.escape(doc)))
            for base in cls.__bases__:
                if issubclass(base, Device):
                    _list(base)
        _list(dev.__class__)
        ret.append('</table>')
        return ''.join(ret)

    def gen_helptarget(self, target):
        if target == 'index':
            return self.gen_helpindex()
        elif target in session.help_topics:
            return self.gen_helptopic(target)
        elif target.startswith('topic:'):
            topicname = target[6:]
            return self.gen_helptopic(topicname)
        elif target.startswith('cmd:'):
            cmdname = target[4:]
            obj = session.namespace[cmdname]
            return self.gen_funchelp(obj)
        elif target.startswith('dev:'):
            devname = target[4:]
            obj = session.devices[devname]
            return self.gen_devhelp(obj)
        elif target.startswith('method:'):
            dev = target[7:].split('.')[0]
            method = target[target.index('.') + 1:]
            return self.gen_methodhelp(getattr(session.devices[dev], method),
                                       dev)
        elif target in session.devices:
            obj = session.devices[target]
            return self.gen_devhelp(obj)
        elif target in session.namespace:
            obj = session.namespace[target]
            return self.gen_funchelp(obj)
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
            '<pre>' + html.escape(ret) + '</pre>'

    def generate(self, obj):
        if obj is None:
            obj = 'index'
        if isinstance(obj, str) and obj not in self._specialtopics:
            return obj, self.header + self.gen_helptarget(obj) + self.footer
        elif isinstance(obj, Device):
            return 'dev:%s' % obj, \
                self.header + self.gen_devhelp(obj) + self.footer
        elif inspect.ismethod(obj) and hasattr(obj, 'is_usermethod'):
            return ('method:%s' % obj.__name__,
                    self.header +
                    self.gen_methodhelp(obj, obj.__self__.name) +
                    self.footer)
        elif inspect.isfunction(obj):
            return 'cmd:%s' % obj.__name__, \
                self.header + self.gen_funchelp(obj) + self.footer
        else:
            return '', \
                self.header + self.gen_genericdoc(obj) + self.footer

    def gen_helptopic(self, obj):
        ret = []
        ret.append(self.gen_heading('Additional help for %s.' % obj, 'help_topics'))
        ret.append(self.gen_markup(session.help_topics[obj]))
        return ''.join(ret)

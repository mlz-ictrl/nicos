#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM command-line GUI client
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICM command-line GUI client."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import glob
import getpass
import optparse
import ConfigParser

import urwid
import urwid.escape
import urwid.raw_display
import urwid.curses_display

from nicm.gui.client import NicosClient, STATUS_INBREAK


def focus_item(text):
    return urwid.AttrWrap(urwid.Text(text.rstrip()), None, 'focus')


class GroupBox(urwid.WidgetWrap):
    def __init__(self, w, caption):
        """Draw a line around w, with a caption."""

        utf8decode = urwid.escape.utf8decode
        tline = urwid.Divider(utf8decode("─"))
        bline = urwid.Divider(utf8decode("─"))
        lline = urwid.SolidFill(utf8decode("│"))
        rline = urwid.SolidFill(utf8decode("│"))
        tlcorner = urwid.Text(utf8decode("┌"))
        trcorner = urwid.Text(utf8decode("┐"))
        blcorner = urwid.Text(utf8decode("└"))
        brcorner = urwid.Text(utf8decode("┘"))
        captext = urwid.Text(' ' + caption + ' ')
        top = urwid.Columns([('fixed', 1, tlcorner),
                             tline,
                             ('fixed', len(caption) + 2, captext),
                             ('fixed', 10, tline),
                             ('fixed', 1, trcorner)])
        middle = urwid.Columns([('fixed', 1, lline), w, ('fixed', 1, rline)],
                               box_columns=[0, 2], focus_column=1)
        bottom = urwid.Columns([('fixed', 1, blcorner),
                                bline, ('fixed', 1, brcorner)])
        pile = urwid.Pile([('flow', top), middle, ('flow', bottom)],
                          focus_item=1)
        urwid.WidgetWrap.__init__(self, pile)


class NicosCmdClient(NicosClient):

    def __init__(self, conndata):
        NicosClient.__init__(self)
        self.conndata = conndata
        self.current_script = ''
        self.current_line = -1

        # history handling
        self._history = []
        self._hist_start_text = ''
        self._hist_current = -1
        # completion handling
        self._completions = []
        self._compindex = -1

        self.scriptitems = urwid.SimpleListWalker([])
        self.outputitems = urwid.SimpleListWalker([])

        self.title = urwid.AttrWrap(urwid.Text('NICM - disconnected',
                                               align='center'), 'header')
        self.status = urwid.AttrWrap(urwid.Text(''), 'status')
        self.firstline = urwid.Columns([self.status])
        self.err = urwid.AttrWrap(urwid.Text(''), 'footer')
        self.input = urwid.AttrWrap(urwid.Edit('>>> '), 'input', 'focus')
        self.inputfiller = urwid.Filler(self.input)

        self.scriptbox = urwid.AttrWrap(urwid.ListBox(self.scriptitems), None)
        self.outputbox = urwid.ListBox(self.outputitems)

        self.pile = urwid.Pile([
            ('weight', 2, urwid.Frame(GroupBox(self.scriptbox, 'Script'),
                                      self.firstline)),
            ('weight', 3, GroupBox(self.outputbox, 'Output')),
            ('fixed', 1, self.inputfiller),
        ], focus_item=2)
        self.top = urwid.Frame(self.pile, self.title, self.err)

    def refresh(self):
        self.ui.draw_screen(self.size, self.top.render(self.size, focus=True))

    def initial_update(self):
        allstatus = self.send_command('get_all_status')
        status, script, output, watch = self.unserialize(allstatus)
        self.signal('new_output', output)
        self.signal('processing_request', {'script': script})
        self.signal('new_status', status)

    def signal(self, type, *args):
        if type == 'error':
            self.err.set_text('ERROR: ' + args[0])
        elif type == 'connected':
            self.title.set_text('NICM - connected to %s:%s as %s' %
                                (self.host, self.port, self.conndata['login']))
        elif type == 'disconnected':
            self.title.set_text('NICM - disconnected')
            self.status.set_text('')
        elif type == 'processing_request':
            script = args[0].get('script')
            if script is None:
                return
            if script != self.current_script:
                self.scriptitems[:] = [focus_item('   ' + line)
                                       for line in script.splitlines()]
                self.current_script = script
                self.current_line = -1
        elif type == 'new_status':
            started, status, line = args[0]
            if started:
                if status != STATUS_INBREAK:
                    self.set_status('running')
                else:
                    self.set_status('interrupted')
            else:
                self.set_status('idle')
            if line != self.current_line:
                try:
                    if self.current_line != -1:
                        text = self.scriptitems[self.current_line-1].get_text()[0]
                        self.scriptitems[self.current_line-1].set_text(
                            '   ' + text[3:])
                    if 0 < line <= len(self.scriptitems):
                        text = self.scriptitems[line-1].get_text()[0]
                        self.scriptitems[line-1].set_text('-> ' + text[3:])
                except IndexError:
                    pass
                self.current_line = line
        elif type == 'new_output':
            newtext = args[0]
            if newtext:
                for text in newtext:
                    self.outputitems.append(focus_item(text))
                self.outputbox.set_focus(len(self.outputitems)-1)
                self.outputbox.make_cursor_visible(self.size)

    def ask(self, question, yesno=False, default='', passwd=False):
        if yesno:
            question += ' [y/n] '
        elif default:
            question += ' [%s] ' % default
        else:
            question += ' '
        self.input.set_caption(question)
        self.input.set_edit_text('')
        self.refresh()
        try:
            while 1:
                if not passwd:
                    self.refresh()
                keys = self.ui.get_input()
                for k in keys:
                    if yesno:
                        if k in 'yn':
                            return k
                    else:
                        if k == 'enter':
                            text = self.input.get_edit_text() or default
                            self.input.set_edit_text('')
                            return text
                        else:
                            self.inputfiller.keypress(self.size, k)
        finally:
            self.input.set_caption('>>> ')

    def help(self):
        self.err.set_text('Meta-commands: /break, /cont, /stop, /stop!, '
                          '/reload, /exec <cmd>,\n/e(dit) <filename>, '
                          '/r(un) <filename>, /update <filename>, '
                          '/connect, /disconnect, /q(uit)')

    def command(self, cmd, arg):
        if cmd == 'cmd':
            self.send_commands('start_prg', arg)
        elif cmd in ('r', 'run'):
            try:
                code = open(arg).read()
            except Exception, e:
                self.err.set_text('Unable to open file: %s' % e)
                return
            self.send_commands('start_named_prg', arg, code)
        elif cmd == 'update':
            try:
                code = open(arg).read()
            except Exception, e:
                self.err.set_text('Unable to open file: %s' % e)
                return
            self.send_commands('update_prg', code)
        elif cmd in ('e', 'edit'):
            ret = os.system('$EDITOR ' + arg)
            self.ui.clear()
            if ret == 0:
                if self.ask('Run file?', yesno=True) == 'y':
                    return self.command('run', arg)
            else:
                self.refresh()
        elif cmd == 'break':
            self.send_command('break_prg')
        elif cmd == 'cont':
            self.send_command('cont_prg')
        elif cmd == 'stop':
            self.send_command('stop_prg')
        elif cmd == 'stop!':
            self.send_command('emergency_stop')
        elif cmd == 'reload':
            self.send_command('reload_modules')
        elif cmd == 'exec':
            self.send_commands('exec_cmd', arg)
        elif cmd == 'disconnect':
            if self.connected:
                self.disconnect()
        elif cmd == 'connect':
            if self.connected:
                self.err.set_text('Already connected!')
            else:
                hostport = '%s:%s' % (self.conndata['host'],
                                      self.conndata['port'])
                server = self.ask('Server host:port?', default=hostport)
                try:
                    host, port = server.split(':', 1)
                    port = int(port)
                except ValueError:
                    pass
                self.conndata['host'] = host
                self.conndata['port'] = port
                user = self.ask('User name?', default=self.conndata['login'])
                self.conndata['login'] = user
                passwd = self.ask('Password?', passwd=True)
                self.conndata['passwd'] = passwd
                self.connect(self.conndata)
        elif cmd in ('q', 'quit'):
            self.disconnect()
            return 0   # exit
        elif cmd in ('h', 'help'):
            self.help()
        else:
            self.err.set_text('Unknown command: %s' % cmd)

    def _histkey(self, key):
        if key == 'up':
            # go earlier
            if self._hist_current == -1:
                self._hist_start_text = self.input.get_edit_text()
                self._hist_current = len(self._history)
            self._histstep(-1)
        elif key == 'down':
            # go later
            if self._hist_current == -1:
                return
            self._histstep(1)
        elif key == 'enter':
            # accept - add to history and do normal processing
            self._hist_current = -1
            text = str(self.input.get_edit_text())
            if text and (not self._history or self._history[-1] != text):
                # append to history, but only if it isn't equal to the last one
                self._history.append(text)

    def _histstep(self, num):
        self._hist_current += num
        if self._hist_current <= -1:
            # no further
            self._hist_current = 0
            return
        if self._hist_current >= len(self._history):
            # back to start
            self._hist_current = -1
            self.input.set_edit_text(self._hist_start_text)
            self.input.set_edit_pos(len(self._hist_start_text))
            return
        self.input.set_edit_text(self._history[self._hist_current])
        self.input.set_edit_pos(len(self._history[self._hist_current]))

    def _completefn(self, text):
        if self._completions:
            self._compindex = (self._compindex + 1) % len(self._completions)
            newtext = self._completions[self._compindex]
        else:
            try:
                cmd, fn = text.split(None, 1)
            except ValueError:
                return
            newtext = ''
            globs = glob.glob(fn + '*')
            if len(globs) == 1:
                newtext = cmd + ' ' + globs[0]
                if os.path.isdir(globs[0]):
                    newtext += '/'
            else:
                prefix = os.path.commonprefix(globs)
                if prefix:
                    newtext = cmd + ' ' + prefix
                self._completions = [
                    '%s %s%s' % (cmd, g, (os.path.isdir(g) and '/' or ''))
                    for g in globs]
        if newtext:
            self.input.set_edit_text(newtext)
            self.input.set_edit_pos(len(newtext))

    def set_status(self, status):
        self.status.set_text('Status: ' + status)
        self.status.set_attr(status)

    def run(self):
        self.size = self.ui.get_cols_rows()
        self.help()
        self.connect(self.conndata)
        self.initial_update()

        focus = 2
        while 1:
            self.refresh()
            try:
                keys = self.ui.get_input()
            except KeyboardInterrupt:
                self.input.set_edit_text('')
                continue
            for k in keys:
                if k == 'window resize':
                    self.size = self.ui.get_cols_rows()
                elif k == 'enter':
                    self._histkey('enter')
                    cmd = self.input.get_edit_text()
                    self.input.set_edit_text('')
                    self.err.set_text('')
                    if cmd.startswith('/'):
                        args = cmd[1:].split(None, 1) + ['','']
                        ret = self.command(args[0], args[1])
                        if ret is not None:
                            return ret
                    elif not cmd:
                        pass
                    else:
                        self.command('cmd', cmd)
                elif k == 'tab':
                    text = self.input.get_edit_text()
                    if text.startswith('/e') or \
                       text.startswith('/r') or \
                       text.startswith('/update'):
                        # if /edit, /run or /update are there, complete filename
                        self._completefn(text)
                    else:
                        # else tab through the three main widgets
                        focus = (focus + 1) % 3
                    self.pile.set_focus(focus)
                elif k in ('up', 'down'):
                    if self.pile.get_focus() == self.inputfiller:
                        # if in command input, step in history
                        self._histkey(k)
                    else:
                        # else, scroll through the items
                        self.top.keypress(self.size, k)
                elif k == 'ctrl d':
                    if not self.input.get_edit_text():
                        return self.command('quit', '')
                else:
                    self._completions = []
                    self.top.keypress(self.size, k)

    def main(self):
        self.ui = urwid.raw_display.Screen()
        self.ui.register_palette([
            ('header', 'light blue', 'black', ('bold', 'underline')),
            ('footer', 'dark red', 'default', ()),
            ('status', 'light cyan', 'black', ('bold',)),
            ('input', 'white', 'black', ()),
            ('focus',  'yellow', 'dark blue', ('bold',)),
            ('running', 'white', 'dark green', ()),
            ('interrupted', 'white', 'dark red', ()),
            ('idle', 'white', 'light gray', ()),
        ])
        return self.ui.run_wrapper(self.run)


def main(argv):
    parser = optparse.OptionParser(usage='''\
%prog [options]

Defaults can be given in ~/.nicm-gui-cmd, like this:

[connect]
server=localhost:1201
user=admin
passwd=secret
''')
    parser.add_option('-s', '--server', dest='server', metavar='host:port',
                      help='server host/port to connect to')
    parser.add_option('-u', '--user', dest='user',
                      help='username to connect with')

    options, args = parser.parse_args(argv)

    config = ConfigParser.RawConfigParser()
    config.read([os.path.expanduser('~/.nicm-gui-cmd')])
    cfgserver = False
    if options.server is None:
        if config.has_option('connect', 'server'):
            cfgserver = True
            options.server = config.get('connect', 'server')
        else:
            parser.error('server option must be given if not in config file')
    if options.user is None:
        if cfgserver and config.has_option('connect', 'user'):
            options.user = config.get('connect', 'user')
        else:
            options.user = raw_input('User name: ')

    if cfgserver and config.has_option('connect', 'passwd'):
        passwd = config.get('connect', 'passwd')
    else:
        passwd = getpass.getpass('Password for %s on %s: ' %
                                 (options.user, options.server))

    try:
        host, port = options.server.split(':', 1)
    except ValueError:
        host = options.server
        port = 1201
    conndata = {
        'host': host,
        'port': int(port),
        'display': '',
        'login': options.user,
        'gzip': False,
        'passwd': passwd,
    }

    client = NicosCmdClient(conndata)
    return client.main()

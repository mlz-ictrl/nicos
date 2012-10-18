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

"""Simple command-line client for the NICOS daemon."""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import re
import sys
import glob
import time
import fcntl
import struct
import getpass
import termios
import ConfigParser
import ctypes, ctypes.util
from logging import DEBUG, INFO, WARNING, ERROR, FATAL

from nicos.daemon import DEFAULT_PORT
from nicos.daemon.pyctl import STATUS_INBREAK, STATUS_IDLE, STATUS_IDLEEXC
from nicos.daemon.client import NicosClient
from nicos.utils import colorize
from nicos.utils.loggers import ACTION, OUTPUT, INPUT

levels = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING',
          ERROR: 'ERROR', FATAL: 'FATAL'}

def format_time(timeval):
    return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(timeval))

def terminal_size():
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def parse_connection_data(s):
    res = re.match(r"(?:(\w+)@)?([\w.]+)(?::(\d+))?", s)
    if res is None:
        return None
    return res.group(1) or 'guest', res.group(2), \
           int(res.group(3) or DEFAULT_PORT)

# unfortunately we need a few functions not exported by Python's readline module
librl = ctypes.cdll[ctypes.util.find_library('readline')]


class NicosCmdClient(NicosClient):

    def __init__(self, conndata, tsize):
        NicosClient.__init__(self)
        self.conndata = conndata
        self.current_script = ['']
        self.current_line = -1
        self.tsize = tsize
        self.out = sys.stdout
        self.shorthost = conndata['host'].split('.')[0]
        self.set_prompt('disconnected')
        self.in_question = False

        # completion handling (BROKEN)
        self._completions = []
        self._compindex = -1

    def put(self, s, c=None):
        # put a line of text
        if c:
            s = colorize(c, s)
        self.out.write('\r\x1b[K%s\n' % s)
        librl.rl_forced_update_display()
        self.out.flush()

    def initial_update(self):
        allstatus = self.ask('getstatus')
        if allstatus is None:
            return
        status, script, output, watch, setups = allstatus
        for msg in output[-self.tsize[1]:]:
            self.put_message(msg)
        self.signal('processing', {'script': script})
        self.signal('status', status)

    def signal(self, type, *args):
        if type == 'error':
            self.put('# ERROR: ' + args[0], 'red')
        elif type == 'failed':
            self.put('# ERROR: ' + args[0], 'red')
        elif type == 'connected':
            self.put('# Connected to %s:%s as %s.' %
                     (self.host, self.port, self.conndata['login']), 'bold')
            self.initial_update()
        elif type == 'disconnected':
            self.put('# Disconnected from server.', 'bold')
            self.set_status('disconnected')
        elif type == 'processing':
            script = args[0].get('script')
            if script is None:
                return
            script = script.splitlines() or ['']
            if script != self.current_script:
                self.current_script = script
        elif type == 'status':
            status, line = args[0]
            if status == STATUS_IDLE:
                self.set_status('idle')
            elif status == STATUS_IDLEEXC:
                self.set_status('idle', exception=True)
            elif status != STATUS_INBREAK:
                self.set_status('running')
            else:
                self.set_status('interrupted')
            if line != self.current_line:
                #text = self.current_script[self.current_line-1]
                #self.put('now executing line %r' % text.strip(), 'darkgray')
                self.current_line = line
        elif type == 'message':
            self.put_message(args[0])
        elif type == 'clientexec':
            plot_func_path = args[0][0]
            try:
                modname, funcname = plot_func_path.rsplit('.', 1)
                func = getattr(__import__(modname, None, None, [funcname]),
                               funcname)
                func(*args[0][1:])
            except Exception, err:
                self.put('# ERROR during "clientexec": %s' % err, 'red')


    psmap = {'idle': 'idle',
             'running': 'busy',
             'interrupted': 'break',
             'disconnected': 'disconnected'
    }
    pcmap = {'idle': 'blue',
             'running': 'fuchsia',
             'interrupted': 'red',
             'disconnected': 'darkgray'}

    def set_prompt(self, status):
        self.prompt = colorize(self.pcmap[status],
            '\r' + self.shorthost + '[%s] >>> ' % self.psmap[status])

    def put_message(self, msg):
        if msg[0] == 'nicos':
            namefmt = ''
        else:
            namefmt = '%-10s: ' % msg[0]
        timefmt = format_time(msg[1])
        levelno = msg[2]
        if levelno == ACTION:
            self.out.write('\033]0;%s%s\007' % (namefmt, msg[3].rstrip()))
            return
        else:
            if levelno <= DEBUG:
                newtext = colorize('darkgray', namefmt + msg[3].rstrip())
            if levelno <= OUTPUT:
                newtext = namefmt + msg[3].rstrip()
            elif levelno == INPUT:
                newtext = colorize('bold', msg[3].rstrip())
            elif levelno <= WARNING:
                newtext = colorize('fuchsia', timefmt + ' ' + namefmt +
                                   levels[levelno] + ': ' + msg[3].rstrip())
            else:
                newtext = colorize('red', timefmt + ' ' + namefmt +
                                   levels[levelno] + ': ' + msg[3].rstrip())
        self.put(newtext)

    def ask_question(self, question, yesno=False, default='', passwd=False):
        self.in_question = True
        try:
            if yesno:
                question += ' [y/n] '
            elif default:
                question += ' [%s] ' % default
            else:
                question += ' '
            ans = raw_input('\r' + question)
            if not ans:
                ans = default
            if yesno:
                if ans.startswith(('y', 'Y')):
                    return 'y'
                return 'n'
            return ans
        finally:
            self.in_question = False
            librl.rl_set_prompt(self.prompt)

    def help(self):
        self.put('# Meta-commands: /break, /cont, /stop, /stop!, '
                 '/reload, /e(dit) <filename>, '
                 '/r(un) <filename>, /update <filename>, '
                 '/connect, /disconnect, /q(uit)', 'turquoise')

    def command(self, cmd, arg):
        if cmd == 'cmd':
            if self.status != 'idle':
                if self.ask_question('A script is already running, execute anyway?',
                                     yesno=True, default='y') == 'y':
                    self.tell('exec', arg)
            else:
                self.tell('queue', '', arg)
        elif cmd in ('r', 'run'):
            try:
                code = open(arg).read()
            except Exception, e:
                self.put('# ERROR: Unable to open file: %s' % e, 'red')
                return
            self.tell('queue', arg, code)
        elif cmd == 'update':
            try:
                code = open(arg).read()
            except Exception, e:
                self.put('# ERROR: Unable to open file: %s' % e, 'red')
                return
            self.tell('update', code)
        elif cmd in ('e', 'edit'):
            ret = os.system('$EDITOR ' + arg)
            if ret == 0:
                if self.ask_question('Run file?', yesno=True) == 'y':
                    return self.command('run', arg)
            else:
                self.refresh()
        elif cmd == 'break':
            self.tell('break')
        elif cmd == 'cont':
            self.tell('continue')
        elif cmd == 'stop':
            self.tell('stop')
        elif cmd == 'stop!':
            self.tell('emergency')
        elif cmd == 'exec':
            self.tell('exec', arg)
        elif cmd == 'disconnect':
            if self.connected:
                self.disconnect()
        elif cmd == 'connect':
            if self.connected:
                self.put('# ERROR: Already connected. Use /disconnect.', 'red')
            else:
                hostport = '%s:%s' % (self.conndata['host'],
                                      self.conndata['port'])
                server = self.ask_question('Server host:port?', default=hostport)
                try:
                    host, port = server.split(':', 1)
                    port = int(port)
                except ValueError:
                    host = server
                    port = DEFAULT_PORT
                self.conndata['host'] = host
                self.conndata['port'] = port
                user = self.ask_question('User name?', default=self.conndata['login'])
                self.conndata['login'] = user
                passwd = self.ask_question('Password?', passwd=True)
                self.conndata['passwd'] = passwd
                self.shorthost = self.conndata['host'].split('.')[0]
                self.connect(self.conndata)
        elif cmd in ('q', 'quit'):
            self.disconnect()
            return 0   # exit
        elif cmd in ('h', 'help'):
            self.help()
        else:
            self.put('# ERROR: Unknown command %r.' % cmd, 'red')

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

    def set_status(self, status, exception=False):
        self.status = status
        self.set_prompt(status)
        if not self.in_question:
            librl.rl_set_prompt(self.prompt)
        librl.rl_forced_update_display()

    def run(self):
        self.help()
        self.connect(self.conndata)

        while 1:
            try:
                cmd = raw_input(self.prompt)
            except KeyboardInterrupt:
                continue
            except EOFError:
                self.command('quit', '')
                self.out.write('\n')
                return
            if cmd.startswith('/'):
                args = cmd[1:].split(None, 1) + ['','']
                ret = self.command(args[0], args[1])
                if ret is not None:
                    return ret
            elif not cmd:
                pass
            else:
                self.command('cmd', cmd)

    def main(self):
        self.run()


def main(argv):
    help = '''\
Usage: %s user@server:port

Defaults can be given in ~/.nicos-cmd, like this:

[connect]
server=localhost:1301
user=admin
passwd=secret
'''

    server = None
    user = None
    passwd = None

    if argv[1:]:
        cd = parse_connection_data(argv[1])
        server = '%s:%s' % cd[1:3]
        user = cd[0]

    config = ConfigParser.RawConfigParser()
    config.read([os.path.expanduser('~/.nicos-cmd')])
    cfgserver = False
    if server is None:
        if config.has_option('connect', 'server'):
            cfgserver = True
            server = config.get('connect', 'server')
        else:
            print help % argv[0]
            return 1
    if user is None:
        if cfgserver and config.has_option('connect', 'user'):
            user = config.get('connect', 'user')
        else:
            user = raw_input('User name: ')

    if cfgserver and config.has_option('connect', 'passwd'):
        passwd = config.get('connect', 'passwd')
    else:
        passwd = getpass.getpass('Password for %s on %s: ' % (user, server))

    try:
        host, port = server.split(':', 1)
    except ValueError:
        host = server
        port = DEFAULT_PORT
    conndata = {
        'host': host,
        'port': int(port),
        'display': '',
        'login': user,
        'passwd': passwd,
    }

    tsize = terminal_size()
    client = NicosCmdClient(conndata, tsize)
    return client.main()

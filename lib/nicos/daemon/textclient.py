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
import readline
import tempfile
import subprocess
import ConfigParser
import ctypes, ctypes.util
from os import path
from logging import DEBUG, INFO, WARNING, ERROR, FATAL

from nicos.daemon import DEFAULT_PORT
from nicos.daemon.pyctl import STATUS_INBREAK, STATUS_IDLE, STATUS_IDLEEXC
from nicos.daemon.client import NicosClient
from nicos.utils import colorize, which, formatDuration, formatEndtime
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

DEFAULT_BINDINGS = '''\
tab: complete
"\\e[5~": history-search-backward
"\\e[6~": history-search-forward
"\\e[1;3D": backward-word
"\\e[1;3C": forward-word
'''


class NicosCmdClient(NicosClient):

    def __init__(self, conndata):
        NicosClient.__init__(self)
        self.conndata = conndata
        self.current_script = ['']
        self.current_line = -1
        self.current_filename = ''
        self.tsize = terminal_size()
        self.out = sys.stdout
        self.browser = None
        self.instrument = conndata['host'].split('.')[0]
        self.in_question = False
        self.in_editing = False
        self.scriptdir = '.'
        self.message_queue = []

        # set up readline
        for line in DEFAULT_BINDINGS.splitlines():
            readline.parse_and_bind(line)
        readline.set_completer(self.completer)
        readline.set_history_length(10000)
        self.histfile = path.expanduser('~/.nicoshistory')
        if path.isfile(self.histfile):
            readline.read_history_file(self.histfile)
        self.completions = []

        self.current_mode = 'master'
        self.set_status('disconnected')

    stcolmap = {'idle': 'blue',
                'running': 'fuchsia',
                'interrupted': 'red',
                'disconnected': 'darkgray'}
    modemap =  {'master': '',
                'slave':  'slave,',
                'simulation': 'simmode,',
                'maintenance': 'maintenance,'}

    def set_prompt(self, status):
        self.prompt = '\x01' + colorize(self.stcolmap[status],
            '\r\x1b[K\x02# ' + self.instrument + '[%s%s] >> \x01' %
            (self.modemap[self.current_mode], status)) + '\x02'

    def set_status(self, status):
        self.status = status
        self.set_prompt(status)
        if not self.in_question:
            librl.rl_set_prompt(self.prompt)
        if not self.in_editing:
            librl.rl_forced_update_display()

    def put(self, s, c=None):
        # put a line of output, preserving the prompt afterwards
        if c:
            s = colorize(c, s)
        self.out.write('\r\x1b[K%s\n' % s)
        librl.rl_forced_update_display()
        self.out.flush()

    def put_error(self, s):
        # put a client error message
        self.put('# ERROR: ' + s, 'red')

    def put_client(self, s):
        # put a client info message
        self.put('# ' + s, 'bold')

    def ask_question(self, question, yesno=False, default='', passwd=False):
        question = '# ' + question
        if passwd:
            return getpass.getpass(colorize('bold', question + ' '))
        self.in_question = True
        try:
            if yesno:
                question += ' [y/n] '
            elif default:
                question += ' [%s] ' % default
            else:
                question += ' '
            try:
                ans = raw_input('\x01\r\x1b[K' + colorize('bold',\
                                    '\x02' + question + '\x01') + '\x02')
                if not ans:
                    ans = default
            except (KeyboardInterrupt, EOFError):
                ans = ''
            if yesno:
                if ans.startswith(('y', 'Y')):
                    return 'y'
                return 'n'
            return ans
        finally:
            self.in_question = False
            librl.rl_set_prompt(self.prompt)

    def initial_update(self):
        allstatus = self.ask('getstatus')
        if allstatus is None:
            return
        status, script, output, watch, setups = allstatus
        for msg in output[-self.tsize[1]:]:
            self.put_message(msg)
        self.put_client('Loaded setups: %s.' % ', '.join(setups))
        self.signal('processing', {'script': script})
        self.signal('status', status)
        self.scriptdir = self.eval('session.experiment.scriptdir', '.')
        self.instrument = self.eval('session.instrument.instrument',
                                    self.instrument)
        self.current_mode = self.eval('session.mode', 'master')
        self.set_status(self.status)

    def signal(self, type, *args):
        try:
            if type == 'error':
                self.put_error(args[0])
            elif type == 'failed':
                self.put_error(args[0])
            elif type == 'connected':
                self.put_client('Connected to %s:%s as %s.' %
                                (self.host, self.port, self.conndata['login']))
                self.initial_update()
            elif type == 'disconnected':
                self.put_client('Disconnected from server.')
                self.current_mode = 'master'
                self.set_status('disconnected')
            elif type == 'processing':
                script = args[0].get('script')
                if script is None:
                    return
                self.current_filename = args[0].get('name', '')
                script = script.splitlines() or ['']
                if script != self.current_script:
                    self.current_script = script
            elif type == 'status':
                status, line = args[0]
                if status == STATUS_IDLE or status == STATUS_IDLEEXC:
                    new_status = 'idle'
                elif status != STATUS_INBREAK:
                    new_status = 'running'
                else:
                    new_status = 'interrupted'
                if status != self.status:
                    self.set_status(new_status)
                if line != self.current_line:
                    self.current_line = line
            elif type == 'message':
                if self.in_editing:
                    self.message_queue.append(args[0])
                else:
                    self.put_message(args[0])
            elif type == 'clientexec':
                self.clientexec(args[0])
            elif type == 'showhelp':
                self.showhelp(args[0][1])
            elif type == 'cache':
                if args[0][1].endswith('/scriptdir'):
                    self.scriptdir = self.eval(
                        'session.experiment.scriptdir', '.')
            elif type == 'simresult':
                timing = args[0][0]
                self.put_client('Simulated minimum runtime: %s (finishes approximately %s).' %
                                (formatDuration(timing), formatEndtime(timing)))
            elif type == 'mode':
                self.current_mode = args[0]
                self.set_status(self.status)
        except Exception, e:
            self.put_error('In event handler: %s.' % e)

    def clientexec(self, what):
        plot_func_path = what[0]
        try:
            modname, funcname = plot_func_path.rsplit('.', 1)
            func = getattr(__import__(modname, None, None, [funcname]),
                           funcname)
            func(*what[1:])
        except Exception, err:
            self.put_error('During "clientexec": %s.' % err)

    def showhelp(self, html):
        fd, fn = tempfile.mkstemp('.html')
        os.write(fd, html)
        os.close(fd)
        if self.browser is None:
            if which('links'):
                self.browser = 'links'
            elif which('w3m'):
                self.browser = 'w3m'
            else:
                self.put_error('No text browser available. '
                               'Install links or w3m.')
                return
        width = str(self.tsize[0])
        self.out.write('\r\x1b[K\n')
        if self.browser == 'links':
            subprocess.Popen(['links', '-dump', '-width', width, fn]).wait()
        else:
            subprocess.Popen(['w3m', '-dump', '-cols', width, fn]).wait()

    def put_message(self, msg):
        if msg[0] == 'nicos':
            namefmt = ''
        else:
            namefmt = '%-10s: ' % msg[0]
        timefmt = format_time(msg[1])
        levelno = msg[2]
        if levelno == ACTION:
            self.out.write('\033]0;NICOS %s%s\007' % (namefmt, msg[3].rstrip()))
            return
        else:
            if levelno <= DEBUG:
                newtext = colorize('darkgray', namefmt + msg[3].rstrip())
            if levelno <= OUTPUT:
                newtext = namefmt + msg[3].rstrip()
            elif levelno == INPUT:
                newtext = colorize('darkgreen', msg[3].rstrip())
                #return
            elif levelno <= WARNING:
                newtext = colorize('purple', timefmt + ' ' + namefmt +
                                   levels[levelno] + ': ' + msg[3].rstrip())
            else:
                newtext = colorize('red', timefmt + ' ' + namefmt +
                                   levels[levelno] + ': ' + msg[3].rstrip())
        self.put(msg[5] + newtext)

    def ask_connect(self, ask_all=True):
        hostport = '%s:%s' % (self.conndata['host'],
                              self.conndata['port'])
        if hostport in (':', ':1301') or ask_all:
            default = '' if hostport in (':', ':1301') else hostport
            server = self.ask_question('Server host:port?', default=default)
            if not server:
                return
            try:
                host, port = server.split(':', 1)
                port = int(port)
            except ValueError:
                host = server
                port = DEFAULT_PORT
            self.conndata['host'] = host
            self.conndata['port'] = port
        if not self.conndata['login'] or ask_all:
            user = self.ask_question('User name?', default=self.conndata['login'])
            self.conndata['login'] = user
        if not self.conndata['passwd'] or ask_all:
            passwd = self.ask_question('Password?', passwd=True)
            self.conndata['passwd'] = passwd
        self.instrument = self.conndata['host'].split('.')[0]
        self.connect(self.conndata)

    def help(self, arg):
        for line in '''\
Meta-commands: /w(here), /log, /break, /cont(inue), /stop,
/e(dit) <file>, /r(un) <file>, /sim(ulate) <file>, /update <file>,
/connect, /disconnect, /q(uit).

Connection defaults can be given on the command-line, e.g.
  nicos-client user@server:port
or in ~/.nicos-cmd, like this:
  [connect]
  server=localhost:1301
  user=admin
  passwd=secret
'''.splitlines():
            self.put('# ' + line, 'turquoise')

    commands = ['queue', 'run', 'simulate', 'edit', 'update', 'break',
                'continue', 'stop', 'where' 'exec', 'disconnect', 'connect',
                'quit', 'help', 'log']

    def print_where(self):
        if self.status in ('running', 'interrupted'):
            self.put_client('Printing current script.')
            for i, line in enumerate(self.current_script):
                if i+1 == self.current_line:
                    self.put(colorize('darkgreen', '---> ' + line))
                else:
                    self.put('     ' + line)
            self.put_client('End of script.')
        else:
            self.put_client('No script is running.')

    def complete_filename(self, fn, text):
        initpath = path.join(self.scriptdir, fn)
        globs = glob.glob(initpath + '*.py')
        return [(f + ('/' if path.isdir(f) else ''))[len(initpath)-len(text):]
                for f in globs]

    def completer(self, text, state):
        if state == 0:
            line = readline.get_line_buffer()
            if line.startswith('/'):
                # client command: complete either command or filename
                parts = line[1:].split()
                if len(parts) < 2 and not line.endswith(' '):
                    self.completions = [cmd for cmd in self.commands
                                        if cmd.startswith(text)]
                else:
                    if parts[0] in ('r', 'run', 'e', 'edit',
                                    'update', 'sim', 'simulate'):
                        try:
                            fn = parts[1]
                        except IndexError:
                            fn = ''
                        self.completions = self.complete_filename(fn, text)
                    else:
                        self.completions = []
            else:
                # server command: ask daemon to complete for us
                try:
                    self.completions = self.ask('complete', text, line)
                except Exception:
                    self.completions = []
        try:
            return self.completions[state]
        except IndexError:
            return None

    def stop_query(self, how):
        self.put_client('== %s ==' % how)
        self.put('# Please enter how to proceed:')
        self.put('# <I> ignore this interrupt')
        self.put('# <H> stop after current step')
        self.put('# <L> stop after current scan')
        self.put('# <S> immediate stop')
        res = self.ask_question('Your choice [I/H/L/S] --->').upper()[:1]
        if res == 'I':
            return
        elif res == 'H':
            self.tell('stop', '2')
        elif res == 'L':
            self.tell('stop', '1')
        else:
            self.tell('emergency')

    def command(self, cmd, arg):
        if cmd == 'cmd':
            if self.status in ('running', 'interrupted'):
                reply = self.ask_question('A script is already running, '
                                          'execute anyway? [y/n/q]', default='y')
                reply = reply.lower()[:1]
                if reply == 'y':
                    self.tell('exec', arg)
                elif reply == 'q':
                    self.tell('queue', '', arg)
                    self.put_client('Command queued.')
            else:
                self.tell('queue', '', arg)
        elif cmd == 'queue':
            self.tell('queue', '', arg)
        elif cmd in ('r', 'run'):
            if not arg:
                self.put_error('Need a file name as argument.')
                return
            fpath = path.join(self.scriptdir, arg)
            try:
                code = open(fpath).read()
            except Exception, e:
                self.put_error('Unable to open file: %s.' % e)
                return
            if self.status in ('running', 'interrupted'):
                if self.ask_question('A script is already running, queue script?',
                                     yesno=True, default='y') == 'y':
                    self.tell('queue', fpath, code)
            else:
                self.tell('queue', fpath, code)
        elif cmd == 'update':
            if not arg:
                if path.isfile(self.current_filename):
                    arg = self.current_filename
            if not arg:
                self.put_error('Need a file name as argument.')
                return
            fpath = path.join(self.scriptdir, arg)
            try:
                code = open(fpath).read()
            except Exception, e:
                self.put_error('Unable to open file: %s.' % e)
                return
            self.tell('update', code)
        elif cmd in ('sim', 'simulate'):
            if not arg:
                self.put_error('Need a file name or code as argument.')
                return
            fpath = path.join(self.scriptdir, arg)
            if path.isfile(fpath):
                try:
                    code = open(fpath).read()
                except Exception, e:
                    self.put_error('Unable to open file: %s.' % e)
                    return
                self.tell('simulate', fpath, code)
            else:
                self.tell('simulate', '', arg)
        elif cmd in ('e', 'edit'):
            if not arg:
                if path.isfile(self.current_filename):
                    arg = self.current_filename
            if not arg:
               self.put_error('Need a file name as argument.')
               return
            fpath = path.join(self.scriptdir, arg)
            if not os.getenv('EDITOR'):
                os.putenv('EDITOR', 'vi')
            self.in_editing = True
            try:
                ret = os.system('$EDITOR "' + fpath + '"')
            finally:
                self.in_editing = False
                for msg in self.message_queue:
                    self.put_message(msg)
                self.message_queue = []
            if ret == 0 and path.isfile(fpath):
                if self.status == 'running':
                    if fpath == self.current_filename:
                        if self.ask_question('Update running script?',
                                             yesno=True) == 'y':
                            return self.command('update', fpath)
                    else:
                        if self.ask_question('Queue file?', yesno=True) == 'y':
                            return self.command('run', fpath)
                else:
                    if self.ask_question('Run file?', yesno=True) == 'y':
                        return self.command('run', fpath)
        elif cmd == 'break':
            self.tell('break')
        elif cmd in ('cont', 'continue'):
            self.tell('continue')
        elif cmd in ('s', 'stop'):
            if self.status == 'running':
                self.stop_query('Stop request')
            else:
                self.tell('emergency')
        elif cmd == 'exec':
            self.tell('exec', arg)
        elif cmd == 'disconnect':
            if self.connected:
                self.disconnect()
        elif cmd == 'connect':
            if self.connected:
                self.put_error('Already connected. Use /disconnect first.')
            else:
                self.ask_connect(ask_all=(arg != 'init'))
        elif cmd in ('q', 'quit'):
            if self.connected:
                self.disconnect()
            return 0   # exit
        elif cmd in ('h', 'help'):
            self.help(arg)
        elif cmd == 'log':
            if arg:
                n = -int(arg)
            else:
                n = None
            allstatus = self.ask('getstatus')
            self.put_client('Printing %s previous messages.' % (-n if n else 'all'))
            for msg in allstatus[2][n:]:
                self.put_message(msg)
            self.put_client('End of messages.')
        elif cmd in ('w', 'where'):
            self.print_where()
        else:
            self.put_error('Unknown command %r.' % cmd)

    def run(self):
        self.help('')
        self.command('connect', 'init')

        while 1:
            try:
                cmd = raw_input(self.prompt)
            except KeyboardInterrupt:
                if self.status == 'running':
                    self.stop_query('Keyboard interrupt')
                continue
            except EOFError:
                self.command('quit', '')
                self.out.write('\n')
                return
            if cmd.startswith('/'):
                args = cmd[1:].split(None, 1) + ['','']
                ret = self.command(args[0], args[1])
                if ret is not None:
                    self.out.write('\n')
                    return ret
            elif not cmd:
                pass
            else:
                self.command('cmd', cmd)

    def main(self):
        try:
            self.run()
        finally:
            readline.write_history_file(self.histfile)


def main(argv):
    server = user = passwd = ''

    # a connection "profile" can be given by invoking this executable
    # under a different name (via symlink)
    configsection = 'connect'
    if not argv[0].endswith('nicos-client'):
        configsection = path.basename(argv[0])

    # or by "+profile" on the command line (other arguments are
    # interpreted as a connection data string)
    if argv[1:]:
        if argv[1].startswith('+'):
            configsection = argv[1][1:]
        else:
            cd = parse_connection_data(argv[1])
            server = '%s:%s' % cd[1:3]
            user = cd[0]

    config = ConfigParser.RawConfigParser()
    config.read([path.expanduser('~/.nicos-cmd')])

    # check for profile name (given by argv0 or command line)
    # if not present, fall back to default
    if not config.has_section(configsection):
        configsection = 'connect'

    if not server and config.has_option(configsection, 'server'):
        server = config.get(configsection, 'server')
    if not user and config.has_option(configsection, 'user'):
        user = config.get(configsection, 'user')
    if config.has_option(configsection, 'passwd'):
        passwd = config.get(configsection, 'passwd')
    try:
        host, port = server.split(':', 1)
    except ValueError:
        host = server
        port = DEFAULT_PORT
    conndata = {
        'host': host,
        'port': int(port),
        'display': os.getenv('DISPLAY') or '',
        'login': user,
        'passwd': passwd,
    }

    client = NicosCmdClient(conndata)
    return client.main()

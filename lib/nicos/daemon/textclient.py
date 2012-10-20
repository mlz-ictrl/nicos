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
import sys
import glob
import random
import select
import getpass
import readline
import tempfile
import subprocess
import ConfigParser
import ctypes, ctypes.util
from os import path
from time import strftime, localtime
from logging import DEBUG, INFO, WARNING, ERROR, FATAL

from nicos.daemon import DEFAULT_PORT
from nicos.daemon.pyctl import STATUS_INBREAK, STATUS_IDLE, STATUS_IDLEEXC
from nicos.daemon.client import NicosClient
from nicos.utils import colorize, which, formatDuration, formatEndtime, \
    terminalSize, parseConnectionString
from nicos.utils.loggers import ACTION, OUTPUT, INPUT

levels = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING',
          ERROR: 'ERROR', FATAL: 'FATAL'}

# introduce the readline C library to our program
librl = ctypes.cdll[ctypes.util.find_library('readline')]
rl_vcpfunc_t = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

DEFAULT_BINDINGS = '''\
tab: complete
"\\e[5~": history-search-backward
"\\e[6~": history-search-forward
"\\e[1;3D": backward-word
"\\e[1;3C": forward-word
'''

# yay, global state!
readline_result = Ellipsis

@rl_vcpfunc_t
def finish_callback(result):
    """A callback for readline() below that records the final line
    in a global variable.  (For some reason making this a method
    of NicosCmdClient fails.)
    """
    global readline_result
    librl.rl_callback_handler_remove()
    # NULL pointer gives None, which means EOF
    readline_result = result


class NicosCmdClient(NicosClient):

    def __init__(self, conndata):
        NicosClient.__init__(self)
        self.conndata = conndata
        self.current_script = ['']
        self.current_line = -1
        self.current_filename = ''
        self.edit_filename = ''
        self.tsize = terminalSize()
        self.out = sys.stdout
        self.browser = None
        self.instrument = conndata['host'].split('.')[0]
        self.in_question = False
        self.in_editing = False
        self.scriptdir = '.'
        self.message_queue = []
        self.pending_requests = {}
        self.tip_shown = False

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

    def readline(self, prompt, add_history=True):
        """Read a line from the user.

        This function basically reimplements the readline module's
        readline_until_enter_or_signal C function, with the addition
        that we set new prompts and update the display periodically.

        Thanks to ctypes this is possible without a custom C module.
        """
        global readline_result
        librl.rl_callback_handler_install(prompt, finish_callback)
        readline_result = Ellipsis
        while readline_result is Ellipsis:
            if not self.in_question:
                # question has an alternate prompt that never changes
                librl.rl_set_prompt(self.prompt)
            librl.rl_forced_update_display()
            res = select.select([sys.stdin], [], [], 0.01)
            if res[0]:
                librl.rl_callback_read_char()
        if readline_result:
            # add to history, but only if requested and not the same as the
            # previous history entry
            if add_history and readline.get_history_item(
                readline.get_current_history_length() - 1) != readline_result:
                librl.add_history(readline_result)
        elif readline_result is None:
            raise EOFError
        return readline_result

    stcolmap = {'idle': 'blue',
                'running': 'fuchsia',
                'interrupted': 'red',
                'disconnected': 'darkgray'}
    modemap =  {'master': '',
                'slave':  'slave,',
                'simulation': 'simmode,',
                'maintenance': 'maintenance,'}

    def set_prompt(self, status):
        pending = ' (%d pending)' % len(self.pending_requests) \
            if self.pending_requests else ''
        self.prompt = '\x01' + colorize(self.stcolmap[status],
            '\r\x1b[K\x02# ' + self.instrument + '[%s%s]%s >> \x01' %
            (self.modemap[self.current_mode], status, pending)) + '\x02'

    def set_status(self, status):
        self.status = status
        self.set_prompt(status)

    def put(self, s, c=None):
        # put a line of output, preserving the prompt afterwards
        if c:
            s = colorize(c, s)
        self.out.write('\r\x1b[K%s\n' % s)
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
                ans = self.readline('\x01\r\x1b[K' + colorize('bold',\
                                    '\x02' + question + '\x01') + '\x02',
                                    add_history=False)
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
        state = self.ask('getstatus')
        if state is None:
            return
        status, script, output, watch, setups, reqqueue = state[:6]
        for msg in output[-self.tsize[1]:]:
            self.put_message(msg)
        if not self.tip_shown:
            self.put_client('Loaded setups: %s. Enter "/help" for help with '
                            'the client commands.' % ', '.join(setups))
            self.tip_shown = True
        else:
            self.put_client('Loaded setups: %s.' % ', '.join(setups))
        self.signal('processing', {'script': script, 'reqno': 0})
        self.signal('status', status)
        self.scriptdir = self.eval('session.experiment.scriptdir', '.')
        self.instrument = self.eval('session.instrument.instrument',
                                    self.instrument)
        self.current_mode = self.eval('session.mode', 'master')
        for req in reqqueue:
            self.pending_requests[req['reqno']] = req
        self.set_status(self.status)

    def clientexec(self, what):
        """Handles the "clientexec" signal."""
        plot_func_path = what[0]
        try:
            modname, funcname = plot_func_path.rsplit('.', 1)
            func = getattr(__import__(modname, None, None, [funcname]),
                           funcname)
            func(*what[1:])
        except Exception, err:
            self.put_error('During "clientexec": %s.' % err)

    def showhelp(self, html):
        """Handles the "showhelp" signal.

        As we already get HTML, we try to get hold of a text-mode browser
        and let it dump the HTML as text.  Then we print that to the user.
        """
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
        """Handles the "message" signal."""
        if msg[0] == 'nicos':
            namefmt = ''
        else:
            namefmt = '%-10s: ' % msg[0]
        timefmt = strftime('[%Y-%m-%d %H:%M:%S]', localtime(msg[1]))
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

    def signal(self, type, data=None, exc=None):
        """Handles any kind of signal/event sent by the daemon."""
        try:
            # try to order the elifs by frequency
            if type == 'message':
                if self.in_editing:
                    self.message_queue.append(data)
                else:
                    self.put_message(data)
            elif type == 'status':
                status, line = data
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
            elif type == 'cache':
                if data[1].endswith('/scriptdir'):
                    self.scriptdir = self.eval(
                        'session.experiment.scriptdir', '.')
            elif type == 'processing':
                script = data.get('script')
                if script is None:
                    return
                self.current_filename = data.get('name', '')
                script = script.splitlines() or ['']
                if script != self.current_script:
                    self.current_script = script
                self.pending_requests.pop(data['reqno'], None)
                self.set_status(self.status)
            elif type == 'request':
                if 'script' in data:
                    self.pending_requests[data['reqno']] = data
                self.set_status(self.status)
            elif type == 'blocked':
                for reqno in data:
                    self.pending_requests.pop(reqno, None)
                self.put_client('%d script(s) or command(s) removed from '
                                'queue.' % len(data))
                self.show_pending()
                self.set_status(self.status)
            elif type == 'connected':
                self.put_client(
                    'Connected to %s:%s as %s. '
                    'Replaying output (enter "/log" to see more)...' %
                    (self.host, self.port, self.conndata['login']))
                self.initial_update()
            elif type == 'disconnected':
                self.put_client('Disconnected from server.')
                self.current_mode = 'master'
                self.set_status('disconnected')
            elif type == 'clientexec':
                self.clientexec(data)
            elif type == 'showhelp':
                self.showhelp(data[1])
            elif type == 'simresult':
                timing = data[0]
                self.put_client('Simulated minimum runtime: %s '
                                '(finishes approximately %s).' %
                                (formatDuration(timing), formatEndtime(timing)))
            elif type == 'mode':
                self.current_mode = data
                self.set_status(self.status)
            elif type in ('error', 'failed', 'broken'):
                self.put_error(data)
            # and we ignore all other signals
        except Exception, e:
            self.put_error('In event handler: %s.' % e)

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
            user = self.ask_question('User name?',
                                     default=self.conndata['login'])
            self.conndata['login'] = user
        if not self.conndata['passwd'] or ask_all:
            passwd = self.ask_question('Password?', passwd=True)
            self.conndata['passwd'] = passwd
        self.instrument = self.conndata['host'].split('.')[0]
        self.connect(self.conndata)

    def help(self, arg):
        """Implements the "/help" command."""
        if not arg:
            arg = 'main'
        if arg not in HELP:
            arg = 'main'
        helptext = HELP[arg]
        for line in helptext.splitlines():
            self.put('# ' + line)

    def edit_file(self, arg):
        """Implements the "/edit" command."""
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
        if ret != 0 or not path.isfile(fpath):
            return
        # if the editor exited successfully (and the file exists) we try to be
        # smart about offering the user a choice of running, simulating or
        # updating the current script
        self.edit_filename = fpath
        if self.status == 'running':
            if fpath == self.current_filename:
                # current script edited: most likely we want to update it
                if self.ask_question('Update running script?',
                                     yesno=True) == 'y':
                    return self.command('update', fpath)
            else:
                # another script edited: updating will likely fail
                reply = self.ask_question('Queue or simulate file? '
                                          '[q/s/n]').lower()
                if reply == 'q':
                    # this will automatically queue
                    return self.command('run', fpath)
                elif reply == 's':
                    return self.command('sim', fpath)
        else:
            # no script is running at the moment: offer to run it
            reply = self.ask_question('Run or simulate file? [r/s/n]').lower()
            if reply == 'r':
                return self.command('run', fpath)
            elif reply == 's':
                return self.command('sim', fpath)

    def print_where(self):
        """Implements the "/where" command."""
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

    def show_pending(self):
        if not self.pending_requests:
            self.put_client('No scripts or commands are pending.')
            return
        self.put_client('Showing pending scripts or commands. '
                        'Use "/block number" to remove.')
        for reqno, script in sorted(self.pending_requests.iteritems()):
            if 'name' in script and script['name']:
                short = script['name']
            else:
                lines = script['script'].splitlines()
                if len(lines) == 1:
                    short = lines[0]
                else:
                    short = lines[0] + ' ...'
            self.put('# %s  %s' % (colorize('blue', '%4d' % reqno), short))
        self.put_client('End of pending list.')

    def stop_query(self, how):
        """Called on Ctrl-C (if running) or when "/stop" is entered."""
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
            # Stoplevel 2 is "everywhere possible"
            self.tell('stop', '2')
        elif res == 'L':
            # Stoplevel 1 is "everywhere in script, or after a scan"
            self.tell('stop', '1')
        else:
            self.tell('emergency')

    def command(self, cmd, arg):
        """Called when a "/foo" command is entered at the prompt."""
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
        elif cmd in ('r', 'run'):
            if not arg:
                if self.edit_filename:
                    reply = self.ask_question('Run last edited file %r?' %
                                path.basename(self.edit_filename),
                                yesno=True, default='y')
                    if reply == 'y':
                        self.command('run', self.edit_filename)
                        return
                self.put_error('Need a file name as argument.')
                return
            fpath = path.join(self.scriptdir, arg)
            try:
                code = open(fpath).read()
            except Exception, e:
                self.put_error('Unable to open file: %s.' % e)
                return
            if self.status in ('running', 'interrupted'):
                if self.ask_question('A script is already running, '
                    'queue script?', yesno=True, default='y') == 'y':
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
            self.edit_file(arg)
        elif cmd == 'break':
            self.tell('break')
        elif cmd in ('cont', 'continue'):
            self.tell('continue')
        elif cmd in ('s', 'stop'):
            if self.status == 'running':
                self.stop_query('Stop request')
            else:
                self.tell('emergency')
        elif cmd == 'pending':
            self.show_pending()
        elif cmd == 'block':
            if arg != '*':
                # this catches an empty arg as well
                try:
                    arg = int(arg)
                    self.pending_requests[arg]
                except (ValueError, KeyError):
                    self.put_error('Need a pending request number '
                                   '(see "/pending") or "*" to clear all.')
                    return
            self.tell('unqueue', str(arg))
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
            state = self.ask('getstatus')
            self.put_client('Printing %s previous messages.' %
                            (-n if n else 'all'))
            for msg in state[2][n:]:
                self.put_message(msg)
            self.put_client('End of messages.')
        elif cmd in ('w', 'where'):
            self.print_where()
        else:
            self.put_error('Unknown command %r.' % cmd)

    def complete_filename(self, fn, text):
        """Try to complete a script filename."""
        # script filenames are relative to the current scriptdir!
        initpath = path.join(self.scriptdir, fn)
        globs = glob.glob(initpath + '*.py')
        return [(f + ('/' if path.isdir(f) else ''))[len(initpath)-len(text):]
                for f in globs]

    commands = ['run', 'simulate', 'edit', 'update', 'break',
                'continue', 'stop', 'where', 'disconnect', 'connect',
                'quit', 'help', 'log', 'pending', 'block']

    def completer(self, text, state):
        """Try to complete the command line.  Called by readline."""
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

    def run(self):
        """Connect and then run the main read-send-print loop."""
        self.command('connect', 'init')

        while 1:
            try:
                cmd = self.readline(self.prompt)
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
        """Main entry point.  Make sure we save the readline history."""
        try:
            self.run()
        finally:
            readline.write_history_file(self.histfile)


def main(argv):
    server = user = passwd = via = ''

    # to automatically close an SSH tunnel, we execute something on the remote
    # server that takes long enough for the client to connect to the daemon;
    # SSH then keeps the session open until the tunnel is unused, i.e. the
    # client has disconnected -- normally, "sleep" should be available as a
    # dummy remote command, but e.g. on erebos.frm2.tum.de it isn't, so we
    # allow configuring this (but only in the config file, not on the cmdline)
    viacommand = 'sleep 10'

    # a connection "profile" can be given by invoking this executable
    # under a different name (via symlink) ...
    configsection = 'connect'
    if not argv[0].endswith('nicos-client'):
        configsection = path.basename(argv[0])

    config = ConfigParser.RawConfigParser()
    config.read([path.expanduser('~/.nicos-client')])

    # ... or by "profile" on the command line (other arguments are
    # interpreted as a connection data string)
    if argv[1:]:
        if config.has_section(argv[1]):
            configsection = argv[1]
        else:
            cd = parseConnectionString(argv[1], DEFAULT_PORT)
            server = '%s:%s' % cd[2:4]
            user = cd[0]
            passwd = cd[1]
        if argv[3:] and argv[2] == 'via':
            via = argv[3]

    # check for profile name as a config section (given by argv0 or on the
    # command line); if not present, fall back to default
    if not config.has_section(configsection):
        configsection = 'connect'

    # take all connection parameters from the config file if not defined
    # on the command line
    if not server and config.has_option(configsection, 'server'):
        server = config.get(configsection, 'server')
    if not user and config.has_option(configsection, 'user'):
        user = config.get(configsection, 'user')
    if not passwd and config.has_option(configsection, 'passwd'):
        passwd = config.get(configsection, 'passwd')
    if not via and config.has_option(configsection, 'via'):
        via = config.get(configsection, 'via')
    if config.has_option(configsection, 'viacommand'):
        viacommand = config.get(configsection, 'viacommand')

    # split server in host:port components
    try:
        host, port = server.split(':', 1)
        port = int(port)
    except ValueError:
        host = server
        port = DEFAULT_PORT

    # if SSH tunneling is requested, stop here and re-exec after tunnel is
    # set up and running
    if via:
        # use a random (hopefully free) high numbered port on our side
        nport = random.randint(10000, 20000)
        os.execvp('sh', ['sh', '-c',
            'ssh -f -L "%s:%s:%s" "%s" %s && %s "%s:%s@localhost:%s"' %
            (nport, host, port, via, viacommand, argv[0], user, passwd, nport)])

    # this is the connection data format used by nicos.daemon.client
    conndata = {
        'host': host,
        'port': port,
        'display': os.getenv('DISPLAY') or '',
        'login': user,
        'passwd': passwd,
    }

    client = NicosCmdClient(conndata)
    return client.main()

# help texts

HELP = {
    'main': '''\
This is the NICOS command-line client.  You can enter all NICOS commands
at the command line; enter "help()" for an overview of NICOS commands
and devices.

This client supports "meta-commands" beginning with a slash:

  /w(here)    -- print current script and location in it
  /log (n)    -- print more past output, n lines or everything
  /break      -- pause script after next scan step or script command
  /cont(inue) -- continue interrupted script
  /s(top)     -- stop script (you will be prompted how abruptly)
  /q(uit)     -- quit only this client (NICOS will continue running)
  /pending    -- show the currently pending commands
  /block n    -- block a pending command by number

  /e(dit) <file>      -- edit a script file
  /r(un) <file>       -- run a script file
  /sim(ulate) <file>  -- simulate a script file
  /update <file>      -- update running script

  /disconnect  -- disconnect from NICOS daemon
  /connect     -- connect to a NICOS daemon

Command parts in parenteses can be omitted.

All output prefixed with "#" comes from the client.

To learn how to pre-set your connection parameters, enter "/help connect".
''',
    'connect': '''\
Connection defaults can be given on the command-line, e.g.

  nicos-client user@server:port

A SSH tunnel can be automatically set up for you with the following
syntax:

  nicos-client user@server:port via sshuser@host

or in a ~/.nicos-client file, like this:

  [connect]
  server = localhost:1301
  user = admin
  passwd = secret
  via = root@instrumenthost

"Profiles" can be created in the config file with sections named other
than "connect". For example, if a section "tas" exists with entries
"server", "user" etc., these parameters can be used by calling the
command line

  nicos-client tas

or by a symlink to "nicos-client" called "tas".
'''
}

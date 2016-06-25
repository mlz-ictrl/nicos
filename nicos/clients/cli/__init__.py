#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Command-line client for the NICOS daemon."""

import os
import sys
import glob
import time
import errno
import random
import select
import signal
import getpass
import readline
import tempfile
import threading
import subprocess
import ctypes
import ctypes.util
from os import path
from time import strftime, localtime
from logging import DEBUG, INFO, WARNING, ERROR, FATAL

from nicos.clients.base import NicosClient, ConnectionData
from nicos.clients.cli.txtplot import txtplot
from nicos.utils import colorize, which, formatDuration, formatEndtime, \
    terminalSize, parseConnectionString
from nicos.utils.loggers import ACTION, INPUT
from nicos.protocols.daemon import DEFAULT_PORT, STATUS_INBREAK, \
    STATUS_IDLE, STATUS_IDLEEXC, BREAK_AFTER_STEP, BREAK_AFTER_LINE
from nicos.core import SIMULATION, SLAVE, MAINTENANCE, MASTER
from nicos.pycompat import configparser, iteritems, to_encoding


levels = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING',
          ERROR: 'ERROR', FATAL: 'FATAL'}

# disable sending events with potentially large data we don't handle
EVENTMASK = ('livedata', 'liveparams', 'watch', 'dataset', 'datacurve',
             'datapoint', 'clientexec')

# introduce the readline C library to our program (we will use Python's
# binding module where possible, but otherwise call the readline functions
# directly via ctypes)
librl = ctypes.cdll[ctypes.util.find_library('readline')]
rl_vcpfunc_t = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

# some useful default readline keybindings
DEFAULT_BINDINGS = '''\
tab: complete
"\\e[5~": history-search-backward
"\\e[6~": history-search-forward
"\\e[1;3D": backward-word
"\\e[1;3C": forward-word
'''

# yay, global state!
readline_result = Ellipsis


def readline_finish_callback(result):
    """A callback for readline() below that records the final line
    in a global variable.  (For some reason making this a method
    of NicosCmdClient fails.)
    """
    # pylint: disable=global-statement
    global readline_result
    librl.rl_callback_handler_remove()
    # NULL pointer gives None, which means EOF
    readline_result = result

c_readline_finish_callback = rl_vcpfunc_t(readline_finish_callback)


class StateChange(Exception):
    """Raised by readline when changing to/from debugger state."""


class NicosCmdClient(NicosClient):

    def __init__(self, conndata):
        NicosClient.__init__(self, self.put_error)
        # connection data as an object
        self.conndata = conndata
        # whether to suppress printing history and other info on connection
        self.quiet_connect = False
        # various state variables
        self.in_question = False
        self.in_editing = False
        self.tip_shown = False
        self.reconnecting = False
        # current script, line within it and filename of script
        self.current_script = ['']
        self.current_line = -1
        self.current_filename = ''
        # pending requests (i.e. scripts) in the daemon
        self.pending_requests = {}
        # filename of last edited/simulated script
        self.last_filename = ''
        # instrument name from NICOS, pre-filled with server name
        self.instrument = conndata.host.split('.')[0]
        # script directory from NICOS
        self.scriptpath = '.'
        # execution mode of the NICOS session
        self.current_mode = MASTER
        # messages queueing up while the editor is running
        self.message_queue = []
        # whether we have initiated a simulation lately
        self.simulating = False
        # whether a stop is pending
        self.stop_pending = False
        # whether we are in debugging mode
        self.debug_mode = False
        # whether we are in spy mode (entering commands disabled)
        self.spy_mode = False
        # detected text-mode browser for help display
        self.browser = None
        # used for determining how much history to print by default
        self.tsize = terminalSize()
        # output stream to print to
        self.out = sys.stdout

        # set up readline
        for line in DEFAULT_BINDINGS.splitlines():
            readline.parse_and_bind(line)
        readline.set_completer(self.completer)
        readline.set_history_length(10000)
        self.histfile = path.expanduser('~/.nicoshistory')
        if path.isfile(self.histfile):
            readline.read_history_file(self.histfile)
        self.completions = []

        # set up "wakeup" pipe to notify readline of output and changed prompt
        self.wakeup_pipe_r, self.wakeup_pipe_w = os.pipe()

        # pre-set prompt to sane default
        self.set_status('disconnected')

    # -- low-level terminal input/output routines

    def readline(self, prompt, add_history=True):
        """Read a line from the user.

        This function basically reimplements the readline module's
        readline_until_enter_or_signal C function, with the addition
        that we set new prompts and update the display periodically.

        Thanks to ctypes this is possible without a custom C module.
        """
        # pylint: disable=global-statement
        global readline_result
        term_encoding = sys.stdout.encoding or 'utf-8'
        librl.rl_callback_handler_install(to_encoding(prompt, term_encoding),
                                          c_readline_finish_callback)
        readline_result = Ellipsis
        while readline_result is Ellipsis:
            try:
                res = select.select([sys.stdin, self.wakeup_pipe_r], [], [], 1)[0]
            except select.error as e:
                if e.args[0] == errno.EINTR:
                    continue
                librl.rl_callback_handler_remove()
                raise
            except:
                librl.rl_callback_handler_remove()
                raise
            if sys.stdin in res:
                librl.rl_callback_read_char()
            if self.wakeup_pipe_r in res:
                os.read(self.wakeup_pipe_r, 1)
                if not self.in_question:
                    # question has an alternate prompt that never changes
                    librl.rl_set_prompt(to_encoding(self.prompt, term_encoding))
                librl.rl_forced_update_display()
        if readline_result:
            # add to history, but only if requested and not the same as the
            # previous history entry
            if add_history and readline.get_history_item(
                    readline.get_current_history_length()) != readline_result:
                librl.add_history(readline_result)
        elif readline_result is None:
            raise EOFError
        elif readline_result is False:
            raise StateChange
        return readline_result.decode(term_encoding)

    def put(self, string):
        """Put a line of output, preserving the prompt afterwards."""
        self.out.write('\r\x1b[K%s\n' % string)
        self.out.flush()
        os.write(self.wakeup_pipe_w, b' ')

    def put_error(self, string):
        """Put a client error message."""
        self.put(colorize('red', '# ERROR: ' + string))

    def put_client(self, string):
        """Put a client info message."""
        self.put(colorize('bold', '# ' + string))

    def ask_passwd(self, question):
        """Prompt user for a password."""
        return getpass.getpass(colorize('bold', '# %s ' % question))

    def ask_question(self, question, chars='', default='', on_intr=''):
        """Prompt user for input to a question."""
        # add hints of what can be entered
        if chars:
            question += ' (%s)' % ('/'.join(chars.upper()))
        if default:
            question += ' [%s]' % default
        self.in_question = True
        try:
            try:
                # see set_status() for an explanation of the special chars here
                ans = self.readline('\x01\r\x1b[K' + colorize('bold',
                                    '\x02# ' + question + ' \x01') + '\x02',
                                    add_history=False)
            except (KeyboardInterrupt, EOFError):
                return on_intr
            if chars:
                # we accept any string; if it's beginning with one of the chars,
                # that is the result, otherwise it's the default value
                ans = ans.lower()
                for char in chars:
                    if ans.startswith(char):
                        return char
                return default
            if not ans:
                ans = default
            return ans
        finally:
            self.in_question = False

    def ask_input(self, question):
        """Prompt user for a line of input."""
        self.in_question = True
        try:
            try:
                # see set_status() for an explanation of the special chars here
                ans = self.readline('\x01\r\x1b[K' + colorize('bold',
                                    '\x02# ' + question + ' \x01') + '\x02',
                                    add_history=False)
            except (KeyboardInterrupt, EOFError):
                return ''
            return ans
        finally:
            self.in_question = False

    # -- event (signal) handlers

    def initial_update(self):
        """Called after connection is established."""
        # request current full status
        state = self.ask('getstatus')
        if state is None:
            return
        if not self.quiet_connect:
            self.put_client(
                'Connected to %s:%s as %s. '
                'Replaying output (enter "/log" to see more)...' %
                (self.host, self.port, self.conndata.user))
            output = self.ask('getmessages', str(self.tsize[1] - 3))
            for msg in output:
                self.put_message(msg)
            if not self.tip_shown:
                self.put_client('Loaded setups: %s. Enter "/help" for help '
                                'with the client commands.' %
                                (', '.join(state['setups'][1]) or '(none)'))
                self.tip_shown = True
            else:
                self.put_client('Loaded setups: %s.' %
                                (', '.join(state['setups'][1]) or '(none)'))
        else:
            self.put_client('Connected to %s:%s as %s. ' %
                            (self.host, self.port, self.conndata.user))
        self.signal('processing', {'script': state['script'], 'reqno': 0})
        self.signal('status', state['status'])
        self.current_mode = state['mode']
        self.scriptpath = self.eval('session.experiment.scriptpath', '.')
        self.instrument = self.eval('session.instrument.instrument',
                                    self.instrument)
        for req in state['requests']:
            self.pending_requests[req['reqno']] = req
        self.set_status(self.status)

    stcolmap  = {'idle': 'blue',
                 'running': 'fuchsia',
                 'paused': 'red',
                 'disconnected': 'darkgray'}
    modemap   = {MASTER: '',
                 SLAVE:  'slave,',
                 SIMULATION: 'simmode,',
                 MAINTENANCE: 'maintenance,'}

    def set_status(self, status):
        """Update the current execution status, and set a new prompt."""
        self.status = status
        if self.stop_pending:
            pending = ' (stop pending)'
        elif self.pending_requests:
            pending = ' (%d pending)' % len(self.pending_requests)
        else:
            pending = ''
        # \x01/\x02 are markers recognized by readline as "here come"
        # zero-width control characters; ESC[K means "clear whole line"
        self.prompt = '\x01' + colorize(
            self.stcolmap[status],
            '\r\x1b[K\x02# ' + (self.instrument or '') + '[%s%s]%s %s \x01' %
            (self.modemap[self.current_mode], status, pending,
             self.spy_mode and 'spy>' or '>>')) + '\x02'
        os.write(self.wakeup_pipe_w, b' ')

    def showhelp(self, html):
        """Handles the "showhelp" signal.

        As we already get HTML, we try to get hold of a text-mode browser
        and let it dump the HTML as text.  Then we print that to the user.
        """
        # write HTML to a temporary file
        fd, fn = tempfile.mkstemp('.html')
        os.write(fd, html)
        os.close(fd)
        # check for a text browser to convert to text only
        if self.browser is None:
            if which('links'):
                self.browser = 'links'
            elif which('w3m'):
                self.browser = 'w3m'
            else:
                self.put_error('No text browser available. '
                               'Install links or w3m.')
                return
        # run HTML through text browser
        width = str(self.tsize[0])
        self.out.write('\r\x1b[K\n')
        if self.browser == 'links':
            subprocess.Popen(['links', '-dump', '-width', width, fn]).wait()
        else:
            subprocess.Popen(['w3m', '-dump', '-cols', width, fn]).wait()
        # remove tempfile
        try:
            os.unlink(fn)
        except Exception:
            pass

    def put_message(self, msg):
        """Handles the "message" signal."""
        if msg[5] == '(sim) ' and not self.simulating:
            return
        elif msg[5] == '(editorsim) ':
            return
        if msg[0] == 'nicos':
            namefmt = ''
        else:
            namefmt = '%-10s: ' % msg[0]
        levelno = msg[2]
        if levelno == ACTION:
            action = namefmt + msg[3].rstrip()
            self.out.write('\x1b]0;NICOS%s\x07' %
                           (action and ' (%s)' % action or ''))
            return
        else:
            if levelno <= DEBUG:
                timefmt = strftime('[%H:%M:%S] ', localtime(msg[1]))
                newtext = colorize('lightgray', timefmt) + \
                    colorize('darkgray', namefmt + msg[3].rstrip())
            elif levelno <= INFO:
                timefmt = strftime('[%H:%M:%S] ', localtime(msg[1]))
                newtext = colorize('lightgray', timefmt) + namefmt + msg[3].rstrip()
            elif levelno == INPUT:
                newtext = colorize('darkgreen', msg[3].rstrip())
            elif levelno <= WARNING:
                timefmt = strftime('[%Y-%m-%d %H:%M:%S] ', localtime(msg[1]))
                newtext = colorize('purple', timefmt + namefmt +
                                   levels[levelno] + ': ' + msg[3].rstrip())
            else:
                timefmt = strftime('[%Y-%m-%d %H:%M:%S] ', localtime(msg[1]))
                newtext = colorize('red', timefmt + namefmt +
                                   levels[levelno] + ': ' + msg[3].rstrip())
        self.put(msg[5] + newtext)

    # pylint: disable=W0221
    def signal(self, name, data=None, exc=None):
        """Handles any kind of signal/event sent by the daemon."""
        try:
            # try to order the elifs by frequency
            if name == 'message':
                if self.in_editing:
                    self.message_queue.append(data)
                else:
                    self.put_message(data)
            elif name == 'status':
                status, line = data  # pylint:disable=W0633
                if status == STATUS_IDLE or status == STATUS_IDLEEXC:
                    new_status = 'idle'
                    self.stop_pending = False
                elif status != STATUS_INBREAK:
                    new_status = 'running'
                else:
                    new_status = 'paused'
                if status != self.status:
                    self.set_status(new_status)
                if line != self.current_line:
                    self.current_line = line
            elif name == 'cache':
                if data[1].endswith('/scriptpath'):
                    self.scriptpath = self.eval(
                        'session.experiment.scriptpath', '.')
            elif name == 'processing':
                script = data.get('script')
                if script is None:
                    return
                self.current_filename = data.get('name') or ''
                script = script.splitlines() or ['']
                if script != self.current_script:
                    self.current_script = script
                self.pending_requests.pop(data['reqno'], None)
                self.set_status(self.status)
            elif name == 'request':
                if 'script' in data:
                    self.pending_requests[data['reqno']] = data
                self.set_status(self.status)
            elif name == 'blocked':
                removed = [_f for _f in (self.pending_requests.pop(reqno, None)
                                         for reqno in data) if _f]
                if removed:
                    self.put_client('%d script(s) or command(s) removed from '
                                    'queue.' % len(removed))
                    self.show_pending()
                self.set_status(self.status)
            elif name == 'connected':
                self.reconnecting = False
                self.initial_update()
            elif name == 'disconnected':
                self.put_client('Disconnected from server, use /reconnect to '
                                'try reconnecting.')
                self.current_mode = MASTER
                self.debug_mode = False
                self.pending_requests.clear()
                self.set_status('disconnected')
            elif name == 'showhelp':
                self.showhelp(data[1])
            elif name == 'simresult':
                if self.simulating:
                    self.simulating = False
                    timing, devinfo = data  # pylint: disable=W0633
                    if timing < 0:
                        self.put_client('Dry run resulted in an error.')
                        return
                    self.put_client('Simulated minimum runtime: %s '
                                    '(finishes approximately %s). Device ranges:' %
                                    (formatDuration(timing, precise=False),
                                     formatEndtime(timing)))
                    if devinfo:
                        dnwidth = max(map(len, devinfo))
                        sorteditems = sorted(iteritems(devinfo),
                                             key=lambda x: x[0].lower())
                        for devname, (_, dmin, dmax, aliases) in sorteditems:
                            aliascol = 'aliases: ' + ', '.join(aliases) if aliases else ''
                            self.put('#   %-*s: %10s  <->  %-10s %s' %
                                     (dnwidth, devname, dmin, dmax, aliascol))
            elif name == 'mode':
                self.current_mode = data
                self.set_status(self.status)
            elif name == 'setup':
                self.instrument = self.eval('session.instrument.instrument',
                                            self.instrument)
            elif name == 'debugging':
                self.debug_mode = data
                readline_finish_callback(False)
            elif name == 'plugplay':
                if data[0] == 'added':
                    self.put_client('new sample environment detected: load '
                                    'setup %r to activate' % data[1])
                elif data[0] == 'removed':
                    self.put_client('sample environment removed: unload '
                                    'setup %r to clear devices' % data[1])
            elif name == 'broken':
                self.put_error(data)
                self.schedule_reconnect()
            elif name == 'failed':
                if self.reconnecting:
                    self.schedule_reconnect()
                else:
                    self.put_error(data)
            elif name == 'error':
                self.put_error(data)
            # and we ignore all other signals
        except Exception as e:
            self.put_error('In %s event handler: %s.' % (name, e))

    # -- reconnect handling

    def schedule_reconnect(self):
        def reconnect():
            if self.reconnecting:
                self.connect(self.conndata, eventmask=EVENTMASK)
        self.reconnecting = True
        threading.Timer(0.5, reconnect).start()

    # -- command handlers

    def ask_connect(self, ask_all=True):
        hostport = '%s:%s' % (self.conndata.host, self.conndata.port)
        if hostport in (':', ':1301') or ask_all:
            default = '' if hostport in (':', ':1301') else hostport
            default = default or 'localhost'
            server = self.ask_question('Server host:port?', default=default)
            if not server:
                return
            try:
                host, port = server.split(':', 1)
                port = int(port)
            except ValueError:
                host = server
                port = DEFAULT_PORT
            self.conndata.host = host
            self.conndata.port = port
        if not self.conndata.user or ask_all:
            user = self.ask_question('User name?',
                                     default=self.conndata.user or 'guest')
            self.conndata.user = user
        if self.conndata.password is None or ask_all:
            password = self.ask_passwd('Password?')
            self.conndata.password = password
        self.instrument = self.conndata.host.split('.')[0]
        try:
            self.connect(self.conndata, eventmask=EVENTMASK)
        except RuntimeError as err:
            self.put_error('Cannot connect: %s.' % err)

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
        fpath = path.join(self.scriptpath, arg)
        if not os.environ.get('EDITOR'):
            os.environ['EDITOR'] = 'vi'
        self.in_editing = True
        cwd = os.getcwd()
        if path.isdir(self.scriptpath):
            os.chdir(self.scriptpath)
        try:
            ret = os.system('$EDITOR "' + fpath + '"')
        finally:
            os.chdir(cwd)
            self.in_editing = False
            for msg in self.message_queue:
                self.put_message(msg)
            self.message_queue = []
        if ret != 0 or not path.isfile(fpath):
            return
        # if the editor exited successfully (and the file exists) we try to be
        # smart about offering the user a choice of running, simulating or
        # updating the current script
        self.last_filename = fpath
        if self.status == 'running':
            if fpath == self.current_filename:
                # current script edited: most likely we want to update it
                if self.ask_question('Update running script?', chars='yn',
                                     default='n') == 'y':
                    return self.command('update', fpath)
            else:
                # another script edited: updating will likely fail
                reply = self.ask_question('Queue or dry-run file?',
                                          chars='qdn')
                if reply == 'q':
                    # this will automatically queue
                    return self.command('run!', fpath)
                elif reply == 'd':
                    return self.command('sim', fpath)
        else:
            # no script is running at the moment: offer to run it
            reply = self.ask_question('Run or dry-run file?', chars='rdn')
            if reply == 'r':
                return self.command('run', fpath)
            elif reply == 'd':
                return self.command('sim', fpath)

    def print_where(self):
        """Implements the "/where" command."""
        if self.status in ('running', 'paused'):
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
                        'Use "/cancel number" to remove.')
        for reqno, script in sorted(iteritems(self.pending_requests)):
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

    def debug_repl(self):
        """Called to handle remote debugging via Rpdb."""
        self.in_question = True  # suppress prompt changes
        try:
            while self.debug_mode:
                try:
                    cmd = self.readline('\x01\r\x1b[K' + colorize('darkred',
                                        '\x02# (Rpdb) \x01') + '\x02') + '\n'
                except (EOFError, KeyboardInterrupt):
                    cmd = ''
                except StateChange:
                    if not self.debug_mode:
                        return
                self.tell('debuginput', cmd)
        finally:
            self.in_question = False

    def plot_data(self, xterm_mode):
        try:
            xs, ys, _, names = self.eval(
                '__import__("nicos").commands.analyze._getData()[:4]')
            plotlines = txtplot(xs, ys, names[0], names[1], xterm_mode)
        except Exception as err:
            self.put_error('Could not plot: %s.' % str(err))
        else:
            for line in plotlines:
                self.put(line)

    def stop_query(self, how):
        """Called on Ctrl-C (if running) or when "/stop" is entered."""
        self.put_client('== %s ==' % how)
        self.put('# Please enter how to proceed:')
        self.put('# <I> ignore this interrupt')
        self.put('# <H> stop after current scan point')
        self.put('# <L> stop after current command')
        self.put('# <S> immediate stop')
        res = self.ask_question('Your choice?', chars='ihls').upper()
        if res == 'I':
            return
        elif res == 'H':
            # this is basically "stop at any well-defined breakpoint"
            self.tell('stop', BREAK_AFTER_STEP)
            self.stop_pending = True
            self.set_status(self.status)
        elif res == 'L':
            # this is "everywhere after a command in the script"
            self.tell('stop', BREAK_AFTER_LINE)
            self.stop_pending = True
            self.set_status(self.status)
        else:
            self.tell('emergency')

    def command(self, cmd, arg):
        """Called when a "/foo" command is entered at the prompt."""
        # try to order elif cases by frequency
        if cmd in ('cmd', 'exec'):
            if cmd == 'cmd' and self.spy_mode:
                return self.command('eval', arg)
            # this is not usually entered as "/cmd foo", but only "foo"
            if self.status in ('running', 'paused'):
                reply = self.ask_question('A script is already running, '
                                          'queue or execute anyway?', chars='qxn')
                if reply == 'x':
                    self.tell('exec', arg)
                elif reply == 'q':
                    self.run(arg)
                    self.put_client('Command queued.')
            else:
                if arg.startswith(':'):
                    self.simulating = True
                self.run(arg)
        elif cmd in ('r', 'run', 'run!'):
            if not arg:
                # since we remember the last edited file, we can offer
                # running it here
                if self.last_filename:
                    reply = self.ask_question('Run last used file %r?' %
                                              path.basename(self.last_filename),
                                              chars='yn', default='y')
                    if reply == 'y':
                        self.command('run', self.last_filename)
                        return
                self.put_error('Need a file name as argument.')
                return
            fpath = path.join(self.scriptpath, arg)
            try:
                code = open(fpath).read()
            except Exception as e:
                self.put_error('Unable to open file: %s.' % e)
                return
            if self.status in ('running', 'paused') and cmd != 'run!':
                if self.ask_question('A script is already running, '
                                     'queue script?', chars='yn',
                                     default='y') == 'y':
                    self.run(code, fpath)
            else:
                self.run(code, fpath)
        elif cmd == 'update':
            if not arg:
                # always take the current filename, if it still exists
                if path.isfile(self.current_filename):
                    arg = self.current_filename
            if not arg:
                self.put_error('Need a file name as argument.')
                return
            fpath = path.join(self.scriptpath, arg)
            try:
                code = open(fpath).read()
            except Exception as e:
                self.put_error('Unable to open file: %s.' % e)
                return
            reason = self.ask_input('Reason for updating:')
            self.tell('update', code, reason)
        elif cmd in ('sim', 'simulate'):
            if not arg:
                self.put_error('Need a file name or code as argument.')
                return
            fpath = path.join(self.scriptpath, arg)
            self.last_filename = fpath
            # detect whether we have a filename or potential Python code
            if path.isfile(fpath) or fpath.endswith(('.py', '.txt')):
                try:
                    code = open(fpath).read()
                except Exception as e:
                    self.put_error('Unable to open file: %s.' % e)
                    return
                self.simulating = True
                self.tell('simulate', fpath, code, 'sim')
            else:
                self.simulating = True
                self.tell('simulate', '', arg, 'sim')
        elif cmd in ('e', 'edit'):
            self.edit_file(arg)
        elif cmd == 'break':
            self.tell('break', BREAK_AFTER_STEP)
        elif cmd in ('cont', 'continue'):
            self.tell('continue')
        elif cmd in ('s', 'stop'):
            if self.status == 'running':
                self.stop_query('Stop request')
            else:
                self.tell('emergency')
        elif cmd in ('fin', 'finish'):
            self.tell('finish')
        elif cmd == 'pending':
            self.show_pending()
        elif cmd == 'cancel':
            if arg != '*':
                # this catches an empty arg as well
                try:
                    arg = int(arg)
                    self.pending_requests[arg]  # pylint: disable=W0104
                except (ValueError, KeyError):
                    self.put_error('Need a pending request number '
                                   '(see "/pending") or "*" to clear all.')
                    return
            self.tell('unqueue', str(arg))
        elif cmd == 'disconnect':
            if self.connected:
                self.disconnect()
        elif cmd == 'connect':
            self.reconnecting = False
            if self.connected:
                self.put_error('Already connected. Use /disconnect first.')
            else:
                self.ask_connect()
        elif cmd in ('re', 'reconnect'):
            self.reconnecting = False   # not automatically, at least
            if self.connected:
                self.disconnect()
            self.ask_connect(ask_all=False)
        elif cmd in ('q', 'quit'):
            if self.connected:
                self.disconnect()
            return 0   # i.e. exit with success
        elif cmd in ('h', 'help', '?'):
            self.help(arg)
        elif cmd == 'log':
            if arg:
                n = str(int(arg))  # make sure it's an integer
            else:
                n = '*'  # as a slice index, this means "unlimited"
            # this can take a while to transfer, but we don't want to cache
            # messages in this client just for this command
            messages = self.ask('getmessages', n)
            if messages is None:
                return
            self.put_client('Printing %s previous messages.' %
                            (n if n != '*' else 'all'))
            for msg in messages:
                self.put_message(msg)
            self.put_client('End of messages.')
        elif cmd in ('w', 'where'):
            self.print_where()
        elif cmd == 'wait':
            if arg:
                time.sleep(float(arg))
            else:
                # this command is mainly meant for testing and scripting purposes
                time.sleep(0.1)
                while self.status != 'idle':
                    time.sleep(0.1)
        elif cmd == 'trace':
            trace = self.ask('gettrace')
            if trace is None:
                return
            self.put_client('Current stacktrace of script execution:')
            for line in trace.splitlines():
                if line:
                    self.put('# ' + line)
            self.put_client('End of stacktrace.')
        elif cmd == 'debugclient':
            import pdb
            pdb.set_trace()
        elif cmd == 'debug':
            self.tell('debug', arg)
        elif cmd == 'eval':
            timefmt = colorize('lightgray', strftime('[%H:%M:%S]'))
            self.put('%s -> %s' % (timefmt, self.eval(arg, stringify=True),))
        elif cmd == 'spy':
            if not self.spy_mode:
                self.put_client('Spy mode on: normal input is evaluated as '
                                'an expression, use /exec to execute as script.')
            else:
                self.put_client('Spy mode off.')
            self.spy_mode = not self.spy_mode
            self.set_status(self.status)
        elif cmd == 'plot':
            self.plot_data(xterm_mode=(arg == 'x'))
        else:
            self.put_error('Unknown command %r.' % cmd)

    # -- command-line completion support

    def complete_filename(self, fn, word):
        """Try to complete a script filename."""
        # script filenames are relative to the current scriptpath; nevertheless
        # the user can override this by giving an absolute path to the script
        initpath = path.join(self.scriptpath, fn)
        candidates = []
        # omit the part already on the line, but not what readline considers the
        # current "word"
        omit = len(initpath) - len(word)
        # complete directories and .py/.txt script files
        for f in glob.glob(initpath + '*'):
            if path.isdir(f):
                candidates.append(f[omit:] + '/')
            elif path.isfile(f) and f.endswith(('.py', '.txt')):
                candidates.append(f[omit:])
        return candidates

    commands = ['run', 'simulate', 'edit', 'update', 'break', 'continue',
                'stop', 'where', 'disconnect', 'connect', 'reconnect',
                'quit', 'help', 'log', 'pending', 'cancel', 'eval', 'spy',
                'plot']

    def completer(self, text, state):
        """Try to complete the command line.  Called by readline."""
        if state == 0:
            # we got a a new bit of text to complete...
            line = readline.get_line_buffer()
            # handle line without command
            if not line.startswith('/'):
                line = '/exec ' + line
            # split into command and arguments
            parts = line[1:].split(None, 1)
            if len(parts) < 2 and not line.endswith(' '):
                # complete client command names
                self.completions = [cmd for cmd in self.commands
                                    if cmd.startswith(text)]
            elif parts[0] in ('r', 'run', 'e', 'edit',
                              'update', 'sim', 'simulate'):
                # complete filenames
                try:
                    fn = parts[1]
                except IndexError:
                    fn = ''
                self.completions = self.complete_filename(fn, text)
            elif parts[0] in ('eval', 'exec'):
                # complete code -- ask the server to complete for us
                try:
                    self.completions = self.ask('complete', text,
                                                parts[1]) or []
                except Exception:
                    self.completions = []
            else:
                # no completions for other commands
                self.completions = []
        try:
            return self.completions[state]
        except IndexError:
            return None

    # -- main loop

    def handle(self, cmd):
        """Handle a command line."""
        # dispatch either as a client command...
        if cmd.startswith('/'):
            args = cmd[1:].split(None, 1) + ['', '']
            return self.command(args[0], args[1])
        elif cmd:
            # or as "normal" Python code to execute
            return self.command('cmd', cmd)
        # an empty line is ignored

    def main(self):
        """Connect and then run the main read-send-print loop."""
        try:
            self.command('reconnect', '')
            while 1:
                try:
                    cmd = self.readline(self.prompt)
                except KeyboardInterrupt:
                    # offer the user a choice of ways of stopping
                    if self.status == 'running' and not self.spy_mode:
                        self.stop_query('Keyboard interrupt')
                    continue
                except EOFError:
                    self.command('quit', '')
                    return 0
                except StateChange:
                    if self.debug_mode:
                        self.debug_repl()
                    continue
                ret = self.handle(cmd)
                if ret is not None:
                    return ret
        finally:
            readline.write_history_file(self.histfile)

    def main_with_command(self, command):
        self.quiet_connect = True
        self.command('reconnect', '')
        self.handle(command)
        time.sleep(0.1)
        while self.status != 'idle':
            time.sleep(0.1)
        self.command('quit', '')
        return 0


# help texts

HELP = {
    'main': '''\
This is the NICOS command-line client.  You can enter all NICOS commands
at the command line; enter "help()" for an overview of NICOS commands
and devices.

This client supports "meta-commands" beginning with a slash:

  /w(here)            -- print current script and location in it
  /log (n)            -- print more past output, n lines or everything
  /break              -- pause script after next scan step or script command
  /cont(inue)         -- continue paused script
  /s(top)             -- stop script (you will be prompted how abruptly)
  /fin(ish)           -- finish current measurement early
  /wait               -- wait until script is finished (for scripting)

  /pending            -- show the currently pending commands
  /cancel n           -- cancel a pending command by number

  /e(dit) <file>      -- edit a script file
  /r(un) <file>       -- run a script file
  /sim(ulate) <file>  -- dry-run a script file
  /update <file>      -- update running script

  /plot               -- plot the current scan in ASCII mode
  /plot x             -- plot the current scan in xterm Tektronix mode

  /disconnect         -- disconnect from NICOS daemon
  /connect            -- connect to a NICOS daemon
  /re(connect)        -- reconnect to NICOS daemon last used
  /q(uit)             -- quit this client (NICOS will continue running)

Command parts in parenteses can be omitted.

All output prefixed with "#" comes from the client.

To learn how to pre-set your connection parameters, enter "/help connect".
To learn about debugging commands, enter "/help debug".
''',
    'connect': '''\
Connection defaults can be given on the command-line, e.g.

  nicos-client user@server:port

A SSH tunnel can be automatically set up for you with the following syntax:

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
''',
    'debug': '''\
There are several debugging commands built into the client:

While a script is running:

  /trace              -- show current stacktrace of script
  /debug              -- put running script into debug mode (pdb);
                         exit using the "c" (continue) command

With no script running:

  /debug code         -- execute some code under remote pdb

At any time:

  /eval expr          -- evaluate expression in script namespace and
                         print the result
  /spy                -- switch into/out of spy mode (regular input
                         is interpreted as /eval)
  /debugclient        -- drop into a pdb shell to debug the client:
                         exit using the "c" command
'''
}


def main(argv):
    server = user = via = command = ''
    password = None

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

    config = configparser.RawConfigParser()
    config.read([path.expanduser('~/.nicos-client')])

    # check for "command to run" switch
    if '-c' in argv:
        n = argv.index('-c')
        if len(argv) >= n:
            command = argv[n+1]
        del argv[n:n+2]

    # ... or by "profile" on the command line (other arguments are
    # interpreted as a connection data string)
    if argv[1:]:
        if config.has_section(argv[1]):
            configsection = argv[1]
        else:
            cd = parseConnectionString(argv[1], DEFAULT_PORT)
            server = '%s:%s' % (cd['host'], cd['port'])
            user = cd['user']
            password = cd['password']
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
    if not password and config.has_option(configsection, 'passwd'):
        password = config.get(configsection, 'passwd')
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
                         'ssh -f -L "%s:%s:%s" "%s" %s && %s "%s%s@localhost:%s"' %
                         (nport, host, port, via, viacommand, argv[0], user,
                          (':%s' % password if password is not None else ''),
                          nport)])

    # don't interrupt event thread's system calls
    signal.siginterrupt(signal.SIGINT, False)

    conndata = ConnectionData(host, port, user, password)
    client = NicosCmdClient(conndata)
    if command:
        return client.main_with_command(command)
    else:
        return client.main()

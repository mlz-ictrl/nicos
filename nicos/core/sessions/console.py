#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

"""Session class for console interface."""

from __future__ import print_function

import os
import pdb
import sys
import code
import signal

try:
    import readline
except ImportError:  # on Windows (without pyreadline)
    readline = None

from nicos import session, nicos_version
from nicos.core import AccessError
from nicos.utils import colorcode, formatExtendedStack
from nicos.utils.loggers import INPUT, INFO
from nicos.core.sessions import Session
from nicos.core.sessions.utils import NicosCompleter
from nicos.core import SIMULATION, SLAVE, MASTER
from nicos.pycompat import input as input_func, exec_


DEFAULT_BINDINGS = '''\
tab: complete
"\\e[5~": history-search-backward
"\\e[6~": history-search-forward
"\\e[1;3D": backward-word
"\\e[1;3C": forward-word
'''


class NicosInteractiveStop(BaseException):
    """
    This exception is raised when the user requests a stop.
    """


class NicosInteractiveConsole(code.InteractiveConsole):
    """
    This class provides a console similar to the standard Python interactive
    console, with the difference that input and output are logged to the
    NICOS logger and will therefore appear in the logfiles.
    """

    def __init__(self, session, global_ns):
        if readline is None:
            raise RuntimeError('The NICOS console cannot run on platforms '
                               'without readline or pyreadline installed.')
        self.session = session
        self.log = session.log
        code.InteractiveConsole.__init__(self, global_ns)
        self.globals = global_ns
        for line in DEFAULT_BINDINGS.splitlines():
            try:
                readline.parse_and_bind(line)
            except IndexError:  # raised by pyreadline if the key is unknown
                pass
        readline.set_completer(session.completefn)
        readline.set_history_length(10000)
        self.histfile = os.path.expanduser('~/.nicoshistory')
        # once compiled, the interactive console uses this flag for all
        # subsequent statements it compiles
        self.compile('from __future__ import division')
        if os.path.isfile(self.histfile):
            readline.read_history_file(self.histfile)

    def interact(self, banner=None):
        signal.signal(signal.SIGINT, self.session.signalHandler)
        signal.signal(signal.SIGTERM, self.sigtermHandler)
        code.InteractiveConsole.interact(self, banner)
        readline.write_history_file(self.histfile)

    def sigtermHandler(self, *args):
        raise SystemExit

    def runsource(self, source, filename='<input>', symbol='single'):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call before runcode().
        """
        try:
            code = self.session.commandHandler(
                source, lambda src: self.compile(src, filename, symbol))
        except Exception:
            self.log.exception('Cannot compile')
            return False

        if code is None:
            return True

        self.log.log(INPUT, '>>> ' + source)
        self.my_runcode(code, source)

        return False

    def raw_input(self, prompt=''):  # pylint: disable=E0202
        sys.stdout.write(colorcode(self.session._pscolor))
        self.session._prompting = True
        try:
            inp = input_func(prompt)
        except KeyboardInterrupt:
            if prompt == sys.ps1:
                # do not stop immediately on continuation lines; here the user
                # usually just wants to abort the input
                print()
                self.session.immediateStop()
                return ''
            else:
                raise
        finally:
            sys.stdout.write(colorcode('reset'))
            self.session._prompting = False
        return inp

    def my_runcode(self, codeobj, source=None):
        """Mostly copied from code.InteractiveInterpreter, but added better
        exception handling.
        """
        session.scriptEvent('start', source)
        try:
            exec_(codeobj, self.globals)
        except NicosInteractiveStop:
            pass
        except KeyboardInterrupt:
            # "immediate stop" chosen
            session.immediateStop()
        except Exception:
            session.scriptEvent('exception', sys.exc_info())
        if hasattr(code, 'softspace') and code.softspace(sys.stdout, 0):
            print()
        session.scriptEvent('finish', None)


class ConsoleSession(Session):
    """
    Subclass of Session that configures the logging system for interactive
    interpreter usage: it adds a console handler with colored output, and
    an exception hook that reports unhandled exceptions via the logging system.
    """

    has_datamanager = True

    def __init__(self, appname, daemonized=False):
        self._console = None
        Session.__init__(self, appname, daemonized)
        # prompt color
        self._pscolor = 'reset'
        # showing prompt?
        self._prompting = False
        # our command completer for Python code
        self._completer = NicosCompleter(self.namespace).complete

    def _initLogging(self, prefix=None, console=True):
        Session._initLogging(self, prefix, console)
        sys.displayhook = self._displayhook

    def _displayhook(self, value):
        if value is not None and getattr(value, '__display__', True):
            self.log.log(INFO, repr(value))

    def loadSetup(self, *args, **kwds):
        Session.loadSetup(self, *args, **kwds)
        self.resetPrompt()

    def setMode(self, mode):
        Session.setMode(self, mode)
        self.resetPrompt()

    def setSPMode(self, on):
        Session.setSPMode(self, on)
        self.resetPrompt()

    def resetPrompt(self):
        base = self._mode != MASTER and self._mode + ' ' or ''
        expsetups = '+'.join(self.explicit_setups)
        sys.ps1 = base + '(%s) %s ' % (expsetups,
                                       '-->' if self._spmode else '>>>')
        sys.ps2 = base + ' %s  ... ' % (' ' * len(expsetups))
        self._pscolor = dict(
            slave='brown',
            master='darkblue',
            maintenance='darkred',
            simulation='turquoise'
        )[self._mode]

    def console(self):
        """Run an interactive console, and exit after it is finished."""
        banner = ('NICOS console ready (version %s).\nTry help() for a '
                  'list of commands, or help(command) for help on a command.'
                  % nicos_version)
        self._console = NicosInteractiveConsole(self, self.namespace)
        self._console.interact(banner)
        sys.stdout.write(colorcode('reset'))

    def completefn(self, word, index):
        if not self._spmode:
            return self._completer(word, index)
        if index == 0:
            line = readline.get_line_buffer()
            self._matches = self._spmhandler.complete(line, word)
        try:
            return self._matches[index] + ' '
        except IndexError:
            return None

    def breakpoint(self, level):
        if session._stoplevel >= level:
            old_stoplevel = session._stoplevel
            session._stoplevel = 0
            raise NicosInteractiveStop(old_stoplevel)

    def immediateStop(self):
        self.log.warning('stopping all devices for immediate stop')
        from nicos.commands.device import stop
        stop()

    def signalHandler(self, signum, frame):
        if self._in_sigint:  # ignore multiple Ctrl-C presses
            return
        if self._prompting:
            # shown while at prompt: always stop directly
            signal.default_int_handler(signum, frame)
        self._in_sigint = True
        try:
            self.log.info('== Keyboard interrupt (Ctrl-C) ==')
            self.log.info('Please enter how to proceed:')
            self.log.info('<I> ignore this interrupt')
            self.log.info('<H> stop after current scan point')
            self.log.info('<L> stop after current scan')
            self.log.info('<S> immediate stop')
            try:
                reply = input_func('---> ')
            except RuntimeError:
                # when already in readline(), this will be raised
                reply = 'S'
            self.log.log(INPUT, reply)
            # first two choices are hidden, but useful for debugging purposes
            if reply.upper() == 'R':
                # handle further Ctrl-C presses with KeyboardInterrupt
                signal.signal(signal.SIGINT, signal.default_int_handler)
            elif reply.upper() == 'D':
                # print a stacktrace and debug
                self.log.info(formatExtendedStack(2))
                pdb.Pdb().set_trace(sys._getframe(1))
            elif reply.upper() == 'I':
                pass
            elif reply.upper() == 'H':
                self._stoplevel = 2
            elif reply.upper() == 'L':
                self._stoplevel = 1
            else:
                # this will create a KeyboardInterrupt and run stop()
                signal.default_int_handler(signum, frame)
        finally:
            self._in_sigint = False

    @classmethod
    def run(cls, setup='startup', simulate=False):
        # Assign the correct class to the session singleton.
        session.__class__ = cls
        session.__init__('nicos')
        session._stoplevel = 0
        session._in_sigint = False

        # Load the initial setup and handle becoming master.
        session.handleInitialSetup(setup, simulate and SIMULATION or SLAVE)

        # Fire up an interactive console.
        try:
            session.console()
        finally:
            # After the console is finished, cleanup.
            if session.mode != SIMULATION:
                session.log.info('shutting down...')
            session.shutdown()

    def checkAccess(self, required):
        # for now, we have no way of knowing who the user is, so we cannot
        # respond to level= keyword
        if 'passcode' in required:
            code = required['passcode']
            if input_func('Please enter "%s" to proceed, or press Enter to '
                          'cancel: ' % code) != code:
                raise AccessError('passcode not correct')
        return Session.checkAccess(self, required)

    def clientExec(self, func, args):
        # the client is the console itself -- just execute it
        func(*args)

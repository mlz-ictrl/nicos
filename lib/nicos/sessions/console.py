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

"""Session class for console interface."""

__version__ = "$Revision$"

import os
import re
import pdb
import sys
import code
import time
import signal
import readline
import traceback
import exceptions

from nicos import session, nicos_version
from nicos.core import AccessError
from nicos.utils import colorcode, formatExtendedStack
from nicos.utils.loggers import INPUT, OUTPUT
from nicos.sessions import Session
from nicos.sessions.utils import NicosCompleter


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

    def __init__(self, session, globals, locals):
        self.session = session
        self.log = session.log
        code.InteractiveConsole.__init__(self, globals)
        self.globals = globals
        self.locals = locals
        readline.parse_and_bind('tab: complete')
        readline.set_completer(NicosCompleter(self.globals).complete)
        readline.set_history_length(10000)
        self.histfile = os.path.expanduser('~/.nicoshistory')
        # once compiled, the interactive console uses this flag for all
        # subsequent statements it compiles
        self.compile('from __future__ import division')
        if os.path.isfile(self.histfile):
            readline.read_history_file(self.histfile)

    def interact(self, banner=None):
        code.InteractiveConsole.interact(self, banner)
        readline.write_history_file(self.histfile)

    def runsource(self, source, filename='<input>', symbol='single'):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call before runcode().
        """
        try:
            code = self.session.commandHandler(source,
                       lambda src: self.compile(src, filename, symbol))
        except (OverflowError, SyntaxError, ValueError):
            self.log.exception()
            return False

        if code is None:
            return True

        self.log.log(INPUT, '>>> ' + source)
        self.runcode(code, source)

        return False

    def raw_input(self, prompt):
        sys.stdout.write(colorcode(self.session._pscolor))
        try:
            inp = raw_input(prompt)
        finally:
            sys.stdout.write(colorcode('reset'))
        return inp

    def runcode(self, codeobj, source=None):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call for exceptions.
        """
        # record starting time to decide whether to send notification
        start_time = time.time()
        # enable session's Ctrl-C interrupt processing
        signal.signal(signal.SIGINT, self.session.signalHandler)
        try:
            exec codeobj in self.globals, self.locals
        except NicosInteractiveStop:
            pass
        except KeyboardInterrupt:
            # "immediate stop" chosen
            session.immediateStop()
        except Exception:
            #raise
            exc_info = sys.exc_info()
            self.session.logUnhandledException(exc_info)
            # also send a notification if configured
            exception = ''.join(traceback.format_exception(*exc_info))
            self.session.notifyConditionally(time.time() - start_time,
                'Exception in script',
                'An exception occurred in the executed script:\n\n' +
                exception, 'error notification',
                short='Exception: ' + exception.splitlines()[-1])
            if exc_info[0] == exceptions.NameError:
                self._guessCorrectCommand(source)
            if exc_info[0] == exceptions.AttributeError:
                self._guessCorrectCommand(source, attribute=True)

            return
        finally:
            # enable own sigint handler again
            signal.signal(signal.SIGINT, signal.default_int_handler)
        if code.softspace(sys.stdout, 0):
            print
        #self.locals.clear()

    def _guessCorrectCommand(self, source, attribute=False):
        """Try to guess the command that was meant by *source*.

        Will do a fuzzy match in all usercommands in the top level namespace and
        tries to find attributes if *attribute* is true.
        """
        if source is None:
            return

        from nicos.utils.comparestrings import compare
        try:
            # extract the first dotted item on the line
            match = re.match('[a-zA-Z_][a-zA-Z0-9_.]*', source)
            if match is None:
                return
            object_parts = match.group(0).split('.')
            if attribute and len(object_parts) < 2:
                return

            # compile a list of existing commands
            allowed_keys = [x for x in self.session._exported_names
                            if hasattr(self.session.namespace[x], 'is_usercommand')]
            allowed_keys += __builtins__.keys()
            allowed_keys += self.locals.keys()
            allowed_keys += self.globals.keys()
            # for attributes, use a list of existing attributes instead
            if attribute:
                obj = None
                if self.globals.has_key(object_parts[0]):
                    obj = self.globals[object_parts[0]]
                if self.locals.has_key(object_parts[0]):
                    obj = self.locals[object_parts[0]]
                for i in range(1, len(object_parts)):
                    try:
                        obj = getattr(obj, object_parts[i])
                    except AttributeError:
                        base = '.'.join(object_parts[:i])
                        poi = object_parts[i]
                        allowed_keys = dir(obj)
                        break
                else:
                    return  # whole object chain exists -- error comes from
                            # somewhere else
            else:
                base = ''
                poi = object_parts[0]

            # compare all allowed keys against given
            comp = {}

            if attribute:
                poi = object_parts[1]
            else:
                poi = object_parts[0]
            for key in allowed_keys:
                if key == poi:
                    return  # the error probably occurred with another object
                            # on the line
                comp[key] = compare(poi, key)
            comp = sorted(comp.items(), key=lambda t: t[1], reverse=True)
            suggestions = [(base and base + '.' or '') + m[0]
                           for m in comp[:3] if m[1] > 2]
            self.session.log.info('Did you mean: %s' % ', '.join(suggestions))
        except Exception:
            pass


class ConsoleSession(Session):
    """
    Subclass of Session that configures the logging system for interactive
    interpreter usage: it adds a console handler with colored output, and
    an exception hook that reports unhandled exceptions via the logging system.
    """

    def __init__(self, appname):
        Session.__init__(self, appname)
        # prompt color
        self._pscolor = 'reset'

    def _initLogging(self):
        Session._initLogging(self)
        sys.displayhook = self._displayhook

    def _displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def loadSetup(self, setupnames, allow_special=False, raise_failed=False):
        Session.loadSetup(self, setupnames, allow_special, raise_failed)
        self.resetPrompt()

    def setMode(self, mode):
        Session.setMode(self, mode)
        self.resetPrompt()

    def resetPrompt(self):
        base = self._mode != 'master' and self._mode + ' ' or ''
        expsetups = '+'.join(self.explicit_setups)
        sys.ps1 = base + '(%s) >>> ' % expsetups
        sys.ps2 = base + ' %s  ... ' % (' ' * len(expsetups))
        self._pscolor = dict(
            slave  = 'brown',
            master = 'darkblue',
            maintenance = 'darkred',
            simulation = 'turquoise'
        )[self._mode]

    def console(self):
        """Run an interactive console, and exit after it is finished."""
        banner = ('NICOS console ready (version %s).\nTry help() for a '
                  'list of commands, or help(command) for help on a command.'
                  % nicos_version)
        console = NicosInteractiveConsole(self,
                                          self.namespace, self.local_namespace)
        console.interact(banner)
        sys.stdout.write(colorcode('reset'))

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
        self._in_sigint = True
        try:
            self.log.info('== Keyboard interrupt (Ctrl-C) ==')
            self.log.info('Please enter how to proceed:')
            self.log.info('<I> ignore this interrupt')
            self.log.info('<H> stop after current step')
            self.log.info('<L> stop after current scan')
            self.log.info('<S> immediate stop')
            try:
                reply = raw_input('---> ')
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

    def forkSimulation(self, code, wait=True):
        try:
            pid = os.fork()
        except OSError:
            self.log.exception('Cannot fork into simulation mode')
            return
        if pid == 0:
            # child process
            signal.alarm(60)   # kill forcibly after 60 seconds
            try:
                self.log.manager.globalprefix = '(sim) '
                self.setMode('simulation')
                exec code in self.namespace
            except:  # really *all* exceptions
                self.log.exception()
            finally:
                sys.exit()
            os._exit()
        # parent process
        if wait:
            try:
                os.waitpid(pid, 0)
            except OSError:
                self.log.exception('Error waiting for simulation process')

    @classmethod
    def run(cls, setup='startup', simulate=False):
        # Assign the correct class to the session singleton.
        session.__class__ = cls
        session.__init__('nicos')
        session._stoplevel = 0
        session._in_sigint = False

        # Load the initial setup and handle becoming master.
        session.handleInitialSetup(setup, simulate)

        # Fire up an interactive console.
        session.console()

        # After the console is finished, cleanup.
        session.log.info('shutting down...')
        session.shutdown()

    def checkAccess(self, required):
        # for now, we have no way of knowing who the user is, so we cannot
        # respond to level= keyword
        if 'passcode' in required:
            code = required['passcode']
            if raw_input('Please enter "%s" to proceed, or press Enter to '
                         'cancel: ' % code) != code:
                raise AccessError('passcode not correct')
        return Session.checkAccess(self, required)

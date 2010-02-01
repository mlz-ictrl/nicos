#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   NICOS interactive interface classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   $Author $
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

"""
Contains the subclass of NICOS specific for running nicm in an interactive
Python shell.
"""

import os
import sys
import code
import readline
import rlcompleter

import nicm
from nicm.interface import NICOS
from nicm.loggers import ColoredConsoleHandler, OUTPUT, INPUT


class NicmInteractiveConsole(code.InteractiveConsole):
    """
    This class provides a console similar to the standard Python interactive
    console, with the difference that input and output are logged to the
    NICOS logger and will therefore appear in the logfiles.
    """

    def __init__(self, nicos, locals):
        self.log = nicos.log
        code.InteractiveConsole.__init__(self, locals)
        readline.parse_and_bind('tab: complete')
        readline.set_completer(rlcompleter.Completer(self.locals).complete)
        readline.set_history_length(10000)
        self.histfile = os.path.expanduser('~/.nicmhistory')
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
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.log.exception('invalid syntax')
            return False

        if code is None:
            return True

        self.log.log(INPUT, source)
        self.runcode(code)
        return False

    def runcode(self, codeobj):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call for exceptions.
        """
        try:
            exec codeobj in self.locals
        except Exception:
            self.log.exception('unhandled exception occurred')
        else:
            if code.softspace(sys.stdout, 0):
                print


class InteractiveNICOS(NICOS):
    """
    Subclass of NICOS that configures the logging system for interactive
    interpreter usage: it adds a console handler with colored output, and
    an exception hook that reports unhandled exceptions via the logging system.
    """

    def _init_logging(self):
        NICOS._init_logging(self)
        self._log_handlers.append(ColoredConsoleHandler())
        # XXX make this conditional
        sys.excepthook = self.__excepthook
        sys.displayhook = self.__displayhook

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def __excepthook(self, etype, evalue, etb):
        if etype is KeyboardInterrupt:
            return
        self.log.error('unhandled exception occurred',
                       exc_info=(etype, evalue, etb))

    def console(self):
        """Run an interactive console, and exit after it is finished."""
        banner = ('NICOS console ready (version %s).\nTry help() for a '
                  'list of commands, or help(command) for help.'
                  % nicm.__version__)
        console = NicmInteractiveConsole(self, self._NICOS__namespace)
        console.interact(banner)
        sys.exit()


def start():
    # Create the NICOS class singleton.
    nicos = nicm.nicos = InteractiveNICOS()

    # Should not be necessary for the separate console.
    #nicos.set_namespace(sys._getframe(1).f_globals)

    # Create the initial instrument setup.
    nicos.load_setup('base')

    # Fire up an interactive console.
    nicos.console()

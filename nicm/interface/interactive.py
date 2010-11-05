#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS interactive interface classes
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

"""
Contains the subclass of NICOS specific for running nicm in an interactive
Python shell.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import sys
import code
import readline
import rlcompleter

import nicm
from nicm.interface import NICOS
from nicm.loggers import ColoredConsoleHandler, OUTPUT, INPUT
from nicm.utils import colorcode


class NicmCompleter(rlcompleter.Completer):
    """
    This is a Completer subclass that doesn't show private attributes when
    completing attribute access.
    """

    def attr_matches(self, text):
        matches = rlcompleter.Completer.attr_matches(self, text)
        textlen = len(text)
        return [m for m in matches if not m[textlen:].startswith(('_', 'do'))]


class NicmInteractiveConsole(code.InteractiveConsole):
    """
    This class provides a console similar to the standard Python interactive
    console, with the difference that input and output are logged to the
    NICOS logger and will therefore appear in the logfiles.
    """

    def __init__(self, nicos, globals, locals):
        self.nicos = nicos
        self.log = nicos.log
        code.InteractiveConsole.__init__(self, globals)
        self.globals = globals
        self.locals = locals
        readline.parse_and_bind('tab: complete')
        readline.set_completer(NicmCompleter(self.globals).complete)
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
            self.log.exception()
            return False

        if code is None:
            return True

        self.log.log(INPUT, source)
        self.runcode(code)
        return False

    def raw_input(self, prompt):
        sys.stdout.write(colorcode('blue'))
        inp = raw_input(prompt)
        sys.stdout.write(colorcode('reset'))
        return inp

    def runcode(self, codeobj):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call for exceptions.
        """
        try:
            exec codeobj in self.globals, self.locals
        except Exception:
            #raise
            self.nicos.logUnhandledException(sys.exc_info())
        else:
            if code.softspace(sys.stdout, 0):
                print
        #self.locals.clear()


class InteractiveNICOS(NICOS):
    """
    Subclass of NICOS that configures the logging system for interactive
    interpreter usage: it adds a console handler with colored output, and
    an exception hook that reports unhandled exceptions via the logging system.
    """

    def _initLogging(self):
        NICOS._initLogging(self)
        self._log_handlers.append(ColoredConsoleHandler())
        sys.displayhook = self.__displayhook

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def console(self):
        """Run an interactive console, and exit after it is finished."""
        banner = ('NICOS console ready (version %s).\nTry help() for a '
                  'list of commands, or help(command) for help.'
                  % nicm.nicm_version)
        console = NicmInteractiveConsole(self, self._NICOS__namespace,
                                         self._NICOS__local_namespace)
        console.interact(banner)
        sys.exit()


def start(setup='startup'):
    # Assign the correct class to the NICOS singleton.
    nicm.nicos.__class__ = InteractiveNICOS
    nicm.nicos.__init__()

    # Should not be necessary for the separate console.
    #nicos.setNamespace(sys._getframe(1).f_globals)

    # Create the initial instrument setup.
    nicm.nicos.loadSetup(setup)

    # Fire up an interactive console.
    nicm.nicos.console()

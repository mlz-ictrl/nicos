#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   NICOS interface classes for running under licos
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
Contains the subclass of NICOS specific for running nicm in the Licos
client/server system.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import sys

try:
    interface = __import__('licos.interface').interface
except ImportError:
    raise ImportError('Not running under Licos, cannot set up interface')

import nicm
from nicm.loggers import OUTPUT
from nicm.interface import NICOS


class LoggingStdout():
    """
    Standard output stream replacement that tees output to a logger.
    """

    def __init__(self, nicos, orig_stdout):
        self.nicos = nicos
        self.orig_stdout = orig_stdout

    def write(self, text):
        self.nicos.log.info(text, nonl=1)
        self.orig_stdout.write(text)

    def flush(self):
        self.orig_stdout.flush()


class LicosNICOS(NICOS):
    """
    Subclass of NICOS that configures the logging system for running under
    Licos: it adds the Licos-provided handler and installs a standard output
    stream that logs stray output.  It also notifies Licos of the logger to
    use for printing scripts ("input") and exceptions.
    """

    def __init__(self):
        NICOS.__init__(self)
        interface.licos_set_logger(self.log)

    def _init_logging(self):
        NICOS._init_logging(self)
        self._log_handlers.append(interface.licos_get_loghandler())
        sys.displayhook = self.__displayhook
        sys.stdout = LoggingStdout(self, sys.stdout)

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))


def start():
    # Create the NICOS class singleton.
    nicos = nicm.nicos = LicosNICOS()

    # NICOS user commands and devices will be placed in the globals of the
    # execution frame that first imports this module.
    nicos.set_namespace(sys._getframe(1).f_globals)

    # Create the initial instrument setup.
    nicos.log.info('--- loading startup setup')
    nicos.load_setup('startup')
    nicos.log.info('--- done')

#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
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

from nicm import nicos
from nicm.loggers import OUTPUT, ColoredConsoleHandler
from nicm.interface import NICOS

from nicm.daemon.util import DaemonLogHandler


class LoggingStdout():
    """
    Standard output stream replacement that tees output to a logger.
    """

    def __init__(self, orig_stdout):
        self.orig_stdout = orig_stdout

    def write(self, text):
        if text.strip():
            nicos.log.info(text)
        self.orig_stdout.write(text)

    def flush(self):
        self.orig_stdout.flush()


class DaemonNICOS(NICOS):
    """
    Subclass of NICOS that configures the logging system for running under the
    execution daemon: it adds the special daemon handler and installs a standard
    output stream that logs stray output.
    """

    def _initLogging(self):
        NICOS._initLogging(self)
        # XXX not if daemonized, please
        self._log_handlers.append(ColoredConsoleHandler())
        sys.displayhook = self.__displayhook
        sys.stdout = LoggingStdout(sys.stdout)

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def daemonSetup(self, daemon):
        nicm_handler = DaemonLogHandler(daemon)
        # add handler to general NICOS logger
        self.log.handlers.append(nicm_handler)
        # and to all loggers created from now on
        self._log_handlers.append(nicm_handler)


def start():
    # Assign the correct class to the NICOS singleton.
    nicos.__class__ = DaemonNICOS
    nicos.__init__()

    # Create the daemon setup and the special device.
    nicos.loadSetup('daemon', allow_special=True)
    daemondev = nicos.getDevice('Daemon')
    nicos.daemonSetup(daemondev)

    # Pretend that the daemon setup doesn't exist, so that another
    # setup can be loaded by the user.
    nicos.devices.clear()
    nicos.explicit_devices.clear()
    nicos.configured_devices.clear()
    nicos.user_modules.clear()
    nicos.loaded_setups.clear()
    del nicos.explicit_setups[:]

    return daemondev

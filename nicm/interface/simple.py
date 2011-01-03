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
Contains the subclass of NICOS specific for running nicm in noninteractive
mode, such as a daemon process.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import sys
import signal

from nicm import nicos
from nicm.utils import writePidfile, removePidfile, daemonize
from nicm.errors import NicmError
from nicm.loggers import ColoredConsoleHandler
from nicm.interface import NICOS


class SimpleNICOS(NICOS):
    """
    Subclass of NICOS that configures the logging system for simple
    noninteractive usage.
    """

    autocreate_devices = False
    auto_modules = []

    def _beforeStart(self, maindev):
        pass

    @classmethod
    def run(cls, appname, maindevname=None, setupname=None, pidfile=True,
            daemon=False, start_args=[]):

        if daemon:
            daemonize()

        nicos.__class__ = cls
        try:
            nicos.__init__(appname)
            nicos.loadSetup(setupname or appname, allow_special=True)
            maindev = nicos.getDevice(maindevname or appname.capitalize())
        except NicmError, err:
            print >>sys.stderr, 'Fatal error while initializing:', err
            return 1

        def signalhandler(signum, frame):
            removePidfile(appname)
            maindev.quit()
        signal.signal(signal.SIGINT, signalhandler)
        signal.signal(signal.SIGTERM, signalhandler)

        if pidfile:
            writePidfile(appname)

        nicos._beforeStart(maindev)

        maindev.start(*start_args)
        maindev.wait()

        nicos.shutdown()

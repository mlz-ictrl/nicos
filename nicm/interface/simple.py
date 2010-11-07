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

import nicm
from nicm.interface import NICOS
from nicm.loggers import ColoredConsoleHandler


class SimpleNICOS(NICOS):
    """
    Subclass of NICOS that configures the logging system for simple
    noninteractive usage.
    """

    auto_modules = []

    def _initLogging(self):
        NICOS._initLogging(self, self.appname)
        self._log_handlers.append(ColoredConsoleHandler())


def start(setup, appname=None):
    # Assign the correct class to the NICOS singleton.
    nicm.nicos.__class__ = SimpleNICOS
    nicm.nicos.appname = appname or setup
    nicm.nicos.__init__()

    # Create the initial nicm setup, and allow special setups.
    nicm.nicos.loadSetup(setup, allow_special=True)

    return nicm.nicos

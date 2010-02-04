#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS test suite
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

"""NICOS test suite."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"


from os import path
from logging import ERROR, Manager, Handler

from nicm import nicos
from nicm import loggers
from nicm.interface import NICOS


class ErrorLogged(Exception):
    """Raised when an error is logged by NICM."""

class TestLogHandler(Handler):
    def emit(self, record):
        if record.levelno >= ERROR:
            if record.exc_info:
                # raise the original exception
                raise record.exc_info[1], None, record.exc_info[2]
            else:
                raise ErrorLogged(record.message)


class TestNICOS(NICOS):
    def __init__(self):
        NICOS.__init__(self)
        self.set_setup_path(path.join(path.dirname(__file__), 'setup'))

    def _init_logging(self):
        loggers.init_loggers()
        self._loggers = {}
        self._log_manager = Manager(None)
        # don't log to a logfile
        self._log_handlers = [TestLogHandler()]


nicos.__class__ = TestNICOS
nicos.__init__()

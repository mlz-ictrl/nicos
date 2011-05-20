#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""NICOS test suite."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
from os import path
from logging import ERROR, Manager, Handler

from nicos import session
from nicos import loggers
from nicos.sessions import Session

class ErrorLogged(Exception):
    """Raised when an error is logged by NICOS."""

class TestLogHandler(Handler):
    def emit(self, record):
        if record.levelno >= ERROR:
            if record.exc_info:
                # raise the original exception
                raise record.exc_info[1], None, record.exc_info[2]
            else:
                raise ErrorLogged(record.message)


class TestSession(Session):
    autocreate_devices = False

    def __init__(self, appname):
        Session.__init__(self, appname)
        self._mode = 'master'
        self.setSetupPath(path.join(path.dirname(__file__), 'setups'))

    def createRootLogger(self, prefix='nicos'):
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        self.log.addHandler(TestLogHandler())

TestSession.config.user = None
TestSession.config.group = None
TestSession.config.control_path = path.join(path.dirname(__file__), 'root')


session.__class__ = TestSession
session.__init__('test')

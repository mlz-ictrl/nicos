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

"""NICOS test suite console."""

import logging
from os import path

try:
    import coverage
except ImportError:
    pass
else:
    # Note: This will only fire up coverage if the COVERAGE_PROCESS_START env
    # variable is set
    coverage.process_startup()

from nicos import config
from nicos.utils import loggers
from nicos.core.sessions.console import ConsoleSession

from test.utils import rootdir, selfDestructAfter


class TestConsoleSession(ConsoleSession):

    def __init__(self, appname, daemonized=False):
        ConsoleSession.__init__(self, appname, daemonized)
        self.setSetupPath(path.join(path.dirname(__file__), 'setups'))

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
        self.log.addHandler(handler)
        self._master_handler = None


config.user = None
config.group = None
config.nicos_root = rootdir

selfDestructAfter(120)
TestConsoleSession.run('startup', False)

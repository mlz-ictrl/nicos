#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""NICOS test suite cache."""

import sys
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
from nicos.core.sessions.simple import NoninteractiveSession

from test.utils import runtime_root, module_root, selfDestructAfter


class TestCacheSession(NoninteractiveSession):

    def __init__(self, appname, daemonized=False):
        NoninteractiveSession.__init__(self, appname, daemonized)
        self.setSetupPath(path.join(module_root, 'test', 'setups'))

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        # show errors on the console
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(
            logging.Formatter('[CACHE] %(name)s: %(message)s'))
        self.log.addHandler(handler)

        handler2 = logging.FileHandler(path.join(runtime_root,
                                                 'cacheserver.log'))
        handler2.setLevel(logging.DEBUG)
        handler2.setFormatter(
            logging.Formatter('[CACHE] %(asctime)s %(name)s: %(message)s'))
        self.log.addHandler(handler2)

config.user = None
config.group = None
config.nicos_root = runtime_root

try:
    setup = sys.argv[1]
except IndexError:
    setup = 'cache'

selfDestructAfter(120)
TestCacheSession.run(setup, 'Server')

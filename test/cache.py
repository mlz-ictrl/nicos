#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

import logging
from os import path

from nicos.utils import loggers
from nicos.sessions.simple import NoninteractiveSession


class TestCacheSession(NoninteractiveSession):

    def __init__(self, appname):
        NoninteractiveSession.__init__(self, appname)
        self.setSetupPath(path.join(path.dirname(__file__), 'setups'))

    def createRootLogger(self, prefix='nicos'):
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        # show errors on the console
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(
            logging.Formatter('[CACHE] %(name)s: %(message)s'))
        self.log.addHandler(handler)

        handler2 = logging.FileHandler(path.join(path.dirname(__file__), 'root','cacheserver.log'))
        handler2.setLevel(logging.DEBUG)
        handler2.setFormatter(
            logging.Formatter('[CACHE] %(asctime)s %(name)s: %(message)s'))
        self.log.addHandler(handler2)

NoninteractiveSession.config.user = None
NoninteractiveSession.config.group = None
NoninteractiveSession.config.control_path = \
    path.join(path.dirname(__file__), 'root')

TestCacheSession.run('cache', 'Server')

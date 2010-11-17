#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS cache device classes
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
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

"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from nicm import status
from nicm.device import Readable, Moveable, Param
from nicm.errors import CommunicationError, TimeoutError


class CacheReader(Readable):

    def doRead(self):
        # cache mechanism already worked its magic, if we end up here
        # there is no valid value in the cache
        raise CommunicationError(self, 'CacheReader value not in cache')

    def doStatus(self):
        # same here as for doRead, however if no status info is in the
        # cache, we assume it's ok
        return status.OK


class CacheWriter(Moveable):

    parameters = {
        'setkey':    Param('Subkey to use to set the device value',
                           type=str, default='setpoint'),
        'window':    Param('Time window for checking stabilization (zero for '
                           'no stabilization check)',
                           unit='s', default=0.0, settable=True),
        'tolerance': Param('Size of the stabilization window',
                           unit='main', default=1.0, settable=True),
        'timeout':   Param('Timeout for checking stabilization',
                           unit='s', default=900.0, settable=True),
        'loopdelay': Param('Sleep time when waiting',
                           unit='s', default=1.0, settable=True),
    }

    def doRead(self):
        raise CommunicationError(self, 'CacheWriter value not in cache')

    def doStatus(self):
        return status.OK

    def doStart(self, pos):
        self._cache.put(self, self.setkey, pos)
        self._goal = pos

    def doWait(self):
        if self.window == 0:
            return
        values = []
        # number of points to check; five points minimum
        histlen = max(int(self.window / self.loopdelay), 5)
        waited = 0
        while len(values) < 5 or \
              max(values) > (self._goal + self.tolerance*0.5) or \
              min(values) < (self._goal - self.tolerance*0.5):
            time.sleep(self.loopdelay)
            waited += self.loopdelay
            values = [self.read()] + values[:histlen]
            self.printdebug('waiting: %s s, values are %s' % (waited, values))
            if waited >= self.timeout:
                raise TimeoutError(self, 'timeout waiting for stabilization')
        return values[0]

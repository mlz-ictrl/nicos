#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

__version__ = "$Revision$"

import time

from nicos import status
from nicos.device import Readable, Moveable, HasLimits, Param
from nicos.errors import CommunicationError, TimeoutError


class CacheReader(Readable):

    def doRead(self):
        raise CommunicationError(self, 'CacheReader value not in cache')

    def doStatus(self):
        return (status.UNKNOWN, 'no status found in cache')


class CacheWriter(HasLimits, Moveable):

    parameters = {
        'setkey':    Param('Subkey to use to set the device value',
                           type=str, default='setpoint'),
        'window':    Param('Time window for checking stabilization (zero for '
                           'no stabilization check)', unit='s', default=0.0,
                           settable=True, category='general'),
        'tolerance': Param('Size of the stabilization window', unit='main',
                           default=1.0, settable=True, category='general'),
        'timeout':   Param('Timeout for checking stabilization',
                           unit='s', default=900.0, settable=True),
        'loopdelay': Param('Sleep time when waiting',
                           unit='s', default=1.0, settable=True),
    }

    def doRead(self):
        raise CommunicationError(self, 'CacheWriter value not in cache')

    def doStatus(self):
        return (status.OK, 'no status found in cache')

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
            self.log.debug('waiting: %s s, values are %s' % (waited, values))
            if waited >= self.timeout:
                raise TimeoutError(self, 'timeout waiting for stabilization')
        return values[0]

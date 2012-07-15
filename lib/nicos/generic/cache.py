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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Cache reader/writer devices."""

__version__ = "$Revision$"

from time import time as currenttime, sleep

from nicos.core import status, Readable, Moveable, HasLimits, Param, \
     CommunicationError, TimeoutError, CacheError


class CacheReader(Readable):
    """A readable device that gets values exclusively via cache.

    This is useful for devices that cannot be usefully integrated into NICOS,
    but that can be coerced to write their current value into the NICOS cache.
    NICOS will then rely on the cache to supply current values for the device;
    if there is no such value in the cache, a `CommunicationError` will be
    raised.  The status is likewise read from the cache; if none is present,
    `status.UNKNOWN` is returned.

    Devices must write into the cache under the keys
    :samp:`nicos/{devname}/value` and :samp:`nicos/{devname}/status`, where
    *devname* is the NICOS device name configured in the setup.
    """

    def doRead(self, maxage=0):
        if self._cache:
            try:
                time, ttl, val = self._cache.get_explicit(self, 'value')
            except CacheError:
                val = time = ttl = None
            if time and ttl and time + ttl < currenttime():
                self.log.warning('value timed out in cache, this should be '
                                 'considered as an error!')
            return val
        raise CommunicationError(self, 'CacheReader value not in cache or '
                                 'no cache found')

    def doStatus(self, maxage=0):
        return status.UNKNOWN, 'no status found in cache'


class CacheWriter(HasLimits, Moveable):
    """A moveable device that writes values via the cache.

    This is the equivalent to `CacheReader` for moveable devices.  The device is
    expected to itself subscribe to cache updates relating to its subkeys, and
    deliver value updates via the cache as well.

    This class will write setpoint changes into the cache under the key
    :samp:`nicos/{devname}/{setkey}`, where *devname* is the NICOS device name,
    and *setkey* is given by the device parameter.
    """

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

    def doRead(self, maxage=0):
        if self._cache:
            try:
                time, ttl, val = self._cache.get_explicit(self, 'value')
            except CacheError:
                val = time = ttl = None
            if time and ttl and time + ttl < currenttime():
                self.log.warning('value timed out in cache, this should be '
                                 'considered as an error!')
            return val
        raise CommunicationError(self, 'CacheWriter value not in cache or '
                                 'no cache found')

    def doStatus(self, maxage=0):
        return status.OK, 'no status found in cache'

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
            sleep(self.loopdelay)
            waited += self.loopdelay
            values = [self.read()] + values[:histlen]
            self.log.debug('waiting: %s s, values are %s' % (waited, values))
            if waited >= self.timeout:
                raise TimeoutError(self, 'timeout waiting for stabilization')
        return values[0]

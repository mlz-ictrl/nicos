#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from time import time as currenttime, sleep
from collections import deque

from nicos.core import status, Readable, Moveable, HasLimits, Param, \
    CommunicationError, TimeoutError, CacheError
from nicos.pycompat import number_types


CACHE_NOSTATUS_STRING = 'no status found in cache'
CACHE_NOVALUE_STRING = 'no value found in cache'


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

    def _get_from_cache(self, name, func, maxage=None):
        """Get *name* from the cache, or call *func* if outdated/not present.

        If the *maxage* parameter is set, do not allow the value to be older
        than that amount of seconds.

        Main difference to global method: do *NOT* write back value to cache
        """
        if not self._cache:
            return func()
        val = None
        if maxage != 0:
            val = self._cache.get(self, name,
                mintime=currenttime() - maxage if maxage is not None else 0)
        if val is None:
            val = func(self.maxage if maxage is None else maxage)
        return val

    def doRead(self, maxage=0):
        if self._cache:
            try:
                time, ttl, val = self._cache.get_explicit(self, 'value')
            except CacheError:
                raise CommunicationError(self, CACHE_NOVALUE_STRING)
            if time and ttl and time + ttl < currenttime():
                # Note: this will only be reached if self.maxage is expired as well
                self.log.warning('value timed out in cache, this should be '
                                 'considered as an error!')
            return val
        raise CommunicationError(self, '%s: no cache found' % self.__class__.__name__)

    def doStatus(self, maxage=0):
        if self._cache:
            try:
                val = self._cache.get_explicit(self, 'status')[2]
            except CacheError:
                val = None
            if val is not None:
                return val
        return status.UNKNOWN, CACHE_NOSTATUS_STRING


class CacheWriter(HasLimits, CacheReader, Moveable):
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
                           'no stabilization check)', unit='s', default=60.0,
                           settable=True, category='general'),
        'tolerance': Param('Size of the stabilization window', unit='main',
                           default=1.0, settable=True, category='general'),
        'timeout':   Param('Timeout for checking stabilization',
                           unit='s', default=900.0, settable=True),
        'loopdelay': Param('Sleep time when waiting',
                           unit='s', default=1.0, settable=True),
    }

    def doStart(self, pos):
        self._cache.put(self, self.setkey, pos)

    def doWait(self):
        if self.window == 0:
            return self.read(0)
        timesout = currenttime() + self.timeout
        histlen = max(int(self.window / self.loopdelay), 5)
        values = deque(maxlen=histlen)

        mystat = self.status(0)

        # is it worth to put his in an extra thread to derive a 'stable' status
        # and give this back in doStatus???
        while True:
            if mystat[0] != status.BUSY and mystat[1] != CACHE_NOSTATUS_STRING:
                break # we got a thrustworthy state of not beeing idle....

            values.append(self.read(0))
            self.log.debug('Values are %r'%list(values))

            if len(values) == histlen:  # enough values ?
                if max(values) - min(values) <= self.tolerance:
                    # we are 'kind of' stable
                    if type(self.target) not in number_types:
                        # stable, but no target to compare with -> OK
                        self.log.debug('Stable but no target given')
                        break
                    elif ( max(values) <= self.target + self.tolerance*0.5 and
                            self.target - self.tolerance*0.5 <= min(values) ):
                        self.log.debug('Value considered stable')
                        break
                    self.log.debug('Value is stable but not within '
                                   '[target-tolerance/2, target+tolerance/2]')

            self.log.debug('Still busy, %ds of %ds left, status is %r' % (
                    timesout-currenttime(), self.timeout, mystat[1]))

            if currenttime() > timesout:
                raise TimeoutError(self, 'timeout waiting for Status!')

            sleep( self.loopdelay )
            mystat = self.status(0)

        return self.read(0)

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************
"""Classes to let devices oscillate."""

from nicos import session
from nicos.core import POLLER, SIMULATION, Attach, ConfigurationError, \
    HasLimits, Moveable, Override, Param, limits, oneof, status, tupleof
from nicos.utils import createThread


class Oscillator(Moveable):
    """Generate an oscillation of a moveable device.

    The moveable must be able to move between the limits.

    to start the oscillation
    >>> move(osc, 'on')

    to stop the oscillation
    >>> move(osc, 'off')

    setting a new range:
    >>> osc.range = (10, 20)
    """

    _targets = ('off', 'on')

    attached_devices = {
        'moveable': Attach('Device to oscillate', Moveable),
    }

    parameters = {
        'range': Param('User defined limits of device value',
                       unit='main', type=limits, settable=True, chatty=True,
                       category='limits', mandatory=False, fmtstr='main'),
        'curvalue': Param('Store the current device value',
                          internal=True, type=oneof(*_targets),
                          settable=True),
        'curstatus': Param('Store the current device status',
                           internal=True, type=tupleof(int, str),
                           settable=True),
        'stoppable': Param("Stop the oscillation via 'stop' command",
                           userparam=True, type=bool, settable=False,
                           default=False),
    }

    parameter_overrides = {
        'unit': Override(default='', settable=False, mandatory=False),
        'fmtstr': Override(default='%s'),
    }

    valuetype = oneof(*_targets)

    hardware_access = False

    _osc_thread = None

    def doInit(self, mode):
        if session.sessiontype != POLLER:  # dont run in the poller!
            self._osc_thread = None
            self._stop_request = False
            # Initialize the status
            self.doStatus()

    def doStart(self, target):
        if self.range[0] == self.range[1]:
            raise ConfigurationError(self, 'No valid range set. Please check!')
        if self._mode == SIMULATION:
            for p in self.range:
                self._attached_moveable._sim_setValue(p)
            return
        self._stop()
        if target == self._targets[1]:
            if not self._osc_thread:
                self.curvalue = self._targets[1]
                self._osc_thread = createThread('oscillation thread %s' % self,
                                                self.__oscillation)
        self.poll()

    def _stop(self):
        self._stop_request = True
        self._attached_moveable.stop()
        if self._osc_thread and self._osc_thread.is_alive():
            self._osc_thread.join()
        self._stop_request = False
        self._osc_thread = None

    def doStop(self):
        if not self.stoppable:
            if self._osc_thread:
                self.log.error("Please use: 'move(%s, %r)' to stop the moving "
                               "device", self, self._targets[0])
                return
        self._stop()

    def doRead(self, maxage=0):
        """Return the current status of the moveable controller."""
        if session.sessiontype != POLLER:
            if self._osc_thread and self._osc_thread.is_alive():
                self.curvalue = self._targets[1]
            else:
                self.curvalue = self._targets[0]
        return self.curvalue

    def doStatus(self, maxage=0):
        """Return the status of the moveable."""
        if session.sessiontype != POLLER:
            if self._osc_thread and not self._osc_thread.is_alive():
                self.curstatus = (status.BUSY, 'moving')
            else:
                self.curstatus = (status.OK, 'idle')
        return self.curstatus

    def doPoll(self, n=0, maxage=0):
        self.pollParams('curvalue', 'curstatus')

    def doReset(self):
        """Reset the moveable controller."""
        self._attached_moveable.reset()

    def doReadRange(self):
        # check range against moveable user limits
        if 'range' in self._config:
            amin, amax = self._config['range']
            if isinstance(self._attached_moveable, HasLimits):
                mmin, mmax = self._attached_moveable.userlimits
                if amin < mmin:
                    raise ConfigurationError(self, 'min (%s) below the '
                                             'moveable min (%s)' % (amin, mmin)
                                             )
                if amax > mmax:
                    raise ConfigurationError(self, 'max (%s) above the '
                                             'moveable max (%s)' % (amax, mmax)
                                             )
        elif isinstance(self._attached_moveable, HasLimits):
            amin, amax = self._attached_moveable.userlimits
        else:
            amin, amax = 0, 0
        return amin, amax

    def doWriteRange(self, r):
        rmin, rmax = r
        if isinstance(self._attached_moveable, HasLimits):
            umin, umax = self._attached_moveable.userlimits
            if rmin < umin:
                raise ConfigurationError(self, 'minimum (%s) below the '
                                         'moveable minimum (%s)' % (rmin, umin)
                                         )
            if rmax > umax:
                raise ConfigurationError(self, 'maximum (%s) above the '
                                         'moveable maximum (%s)' % (rmax, umax)
                                         )
        return rmin, rmax

    def __oscillation(self):
        self.log.info('Oscillation of %r started', self._attached_moveable)
        _range = self.range
        while not self._stop_request:
            for pos in _range:
                self._attached_moveable.maw(pos)
                if self._stop_request:
                    break
        self.curvalue = self._targets[0]
        self.log.info('Oscillation of %r stopped', self._attached_moveable)

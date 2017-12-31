#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Attach, ConfigurationError, Moveable, Override, POLLER,\
    Param, SIMULATION, limits, oneof, status, tupleof
from nicos.core.errors import UsageError
from nicos.utils import createThread


class Oscillator(Moveable):
    """Generate an oscillation of a moveable device.

    The moveable must be able to move between the limits.
    """

    _targets = ('off', 'on')

    attached_devices = {
        'moveable': Attach('Device to oscillate', Moveable),
    }

    parameters = {
        'range': Param('User defined limits of device value',
                       unit='main',
                       type=limits, settable=True, chatty=True,
                       category='limits', mandatory=False, fmtstr='main'),
        'curvalue': Param('Store the current device value',
                          userparam=False, type=oneof(*_targets),
                          settable=True,),
        'curstatus': Param('Store the current device status',
                           userparam=False, type=tupleof(int, str),
                           settable=True,),
        'stoppable': Param("Stop the oscillation via 'stop' command",
                           userparam=True, type=bool, settable=False,
                           default=False,)
    }

    parameter_overrides = {
        'unit': Override(default='', settable=False, mandatory=False),
        'fmtstr': Override(default='%s'),
    }

    valuetype = oneof(*_targets)

    hardware_access = False

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        if session.sessiontype != POLLER:  # dont run in the poller!
            self._osc_thread = None
            self._stop_request = False

    def doStart(self, target):
        if self._mode == SIMULATION:
            for p in self.range:
                self.attached_moveable._sim_setValue(p)
            return
        if target == 'on':
            self._stop()
            self._stop_request = False
            if not self._osc_thread:
                self._osc_thread = createThread('oscillation thread %s' % self,
                                                self.__oscillation)
        else:
            self._stop()
        self.poll()

    def _stop(self):
        self._stop_request = True
        self._attached_moveable.stop()
        if self._osc_thread and self._osc_thread.isAlive():
            self._osc_thread.join()
        self._osc_thread = None

    def doStop(self):
        if self.stoppable:
            self._stop()
        else:
            raise UsageError(self, "Please use: 'move(%s, 'off')' to stop the "
                             "moving device" % self)

    def doRead(self, maxage=0):
        """Return the current status of the moveable controller."""
        if session.sessiontype != POLLER:
            if self._osc_thread and self._osc_thread.isAlive():
                self.curvalue = self._targets[1]
            else:
                self.curvalue = self._targets[0]
        return self.curvalue

    def doStatus(self, maxage=0):
        """Return the status of the moveable."""
        if session.sessiontype != POLLER:
            if self._osc_thread and not self._osc_thread.isAlive():
                self.curstatus = (status.BUSY, 'moving')
            else:
                self.curstatus = (status.OK, 'idle')
        return self.curstatus

    def doPoll(self, n=0, maxage=0):
        self._pollParam('curvalue', 1)
        self._pollParam('curstatus', 1)
        return self.curvalue, self.curstatus

    def doReset(self):
        """Reset the moveable controller."""
        self._attached_moveable.reset()

    def doReadRange(self):
        # check range against moveable user limits
        if 'range' in self._config:
            amin, amax = self._config['range']
            mmin, mmax = self._attached_moveable.userlimits
            if amin < mmin:
                raise ConfigurationError(self, 'min (%s) below the moveable'
                                         ' min (%s)' % (amin, mmin))
            if amax > mmax:
                raise ConfigurationError(self, 'max (%s) above the moveable'
                                         ' max (%s)' % (amax, mmax))
        else:
            amin, amax = self._attached_moveable.userlimits
        return amin, amax

    def doWriteRange(self, r):
        rmin, rmax = r
        umin, umax = self._attached_moveable.userlimits
        if rmin > rmax:
            raise ConfigurationError(self, 'minimum (%s) above the maximum '
                                     '(%s)' % (rmin, rmax))
        if rmin < umin - abs(umin * 1e-12):
            raise ConfigurationError(self, 'minimum (%s) below the moveable '
                                     'minimum (%s)' % (rmin, umin))
        if rmax > umax + abs(umax * 1e-12):
            raise ConfigurationError(self, 'maximum (%s) above the moveable '
                                     'maximum (%s)' % (rmax, umax))

    def __oscillation(self):
        _range = self.range
        while not self._stop_request:
            for pos in _range:
                self._attached_moveable.start(pos)
                self._attached_moveable.wait()
                if self._stop_request:
                    break
        self.log.info('oscillation stopped')

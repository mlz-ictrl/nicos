#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core import Param, pvname, status
from nicos.devices.epics import EpicsAnalogMoveable

from nicos_sinq.devices.epics.generic import WindowMoveable


class ChopperMoveable(WindowMoveable):

    _starting = False

    def doStart(self, target):
        self._starting = True
        self._target = target
        WindowMoveable.doStart(self, target)

    def doStatus(self, maxage=0):
        tg = self._get_pv('targetpv')
        if self._starting:
            if abs(tg - self._target) < self.window:
                self._starting = False
            return status.BUSY, 'starting'
        pos = self.read(0)
        if abs(pos - tg) < self.window:
            return status.OK, 'At target'
        return status.BUSY, 'Moving ...'


class ChopperPhase(WindowMoveable):

    parameters = {
        'dphas': Param('Reading the phase difference',
                       type=pvname, mandatory=True),
        'phase_error': Param('Phase error',
                             type=float, settable=True),
    }

    def _get_pv_parameters(self):
        pvs = WindowMoveable._get_pv_parameters(self)
        pvs.add('dphas')
        return pvs

    def doReadPhase_error(self):
        return self._get_pv('dphas')

    def doStatus(self, maxage=0):
        if self._get_pv('dphas') < self.window:
            return status.OK, 'At target'
        return status.BUSY, 'Moving ...'

    def doStop(self):
        # There is no sensible way to stop
        # a phase change
        pass


class ChopperRatio(EpicsAnalogMoveable):

    def doStop(self):
        # There is no sensible way to stop
        # a ratio change
        pass

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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import epics

from nicos.core import CommunicationError, Override, Param, none_or, status
from nicos.core.mixins import HasLimits, HasPrecision
from nicos.devices.epics.pyepics import EpicsMoveable, EpicsReadable

from nicos_sinq.devices.epics.base import EpicsAnalogMoveableSinq


class WindowMoveable(HasLimits, HasPrecision, EpicsMoveable):
    """
    Some devices do not have a way to determine their status. The only way
    to test for completion is to read the value back and test if it is
    within a certain window of the target. This is done here.
    """

    parameters = {
        # I have to use my private parameter _drive_target to store the target
        # since the marked as volatile in EpicsMoveable and is not holding the
        # real target.
        '_drive_target': Param('Saves a copy of the target',
                               type=none_or(float), internal=True,
                               settable=True)
    }

    parameter_overrides = {
        'target': Override(settable=True),
    }

    valuetype = float

    def doStart(self, target):
        self._drive_target = target
        EpicsMoveable.doStart(self, target)

    def doStatus(self, maxage=0):
        if self._drive_target is not None:
            if not self.isAtTarget(target=self._drive_target):
                return status.BUSY, 'Moving'
            self._drive_target = None
        return status.OK, 'Done'


class EpicsArrayReadable(EpicsReadable):
    parameters = {
        'count': Param('How many array values to read',
                       type=int, mandatory=True),
    }

    def doInit(self, mode):
        EpicsReadable.doInit(self, mode)
        self._sim_setValue([0] * self.count)

    def doRead(self, maxage=0):
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()
        result = self._pvs['readpv'].get(timeout=self.epicstimeout,
                                         count=self.count)
        if result is None:  # timeout
            raise CommunicationError(self, 'timed out getting PV %r from EPICS'
                                     % self._get_pv_name('readpv'))
        return result


class EpicsAnalogMoveable(HasPrecision, EpicsAnalogMoveableSinq):

    def doStatus(self, maxage=0):
        pos = self.doRead(0)
        target = self.doReadTarget()

        if not self.isAtTarget(pos, target):
            return status.BUSY, 'Moving'

        return status.OK, 'Done'

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
import epics

from nicos.core import CommunicationError, Override, Param, status
from nicos.core.mixins import HasLimits
from nicos.devices.epics import EpicsMoveable, EpicsReadable


class WindowMoveable(HasLimits, EpicsMoveable):
    """
    Some devices do not have a way to determine their status. The only way
    to test for completion is to read the value back and test if it is
    within a certain window of the target. This is done here.
    """

    parameters = {
        'window': Param('Tolerance used for testing for completion',
                        type=float,
                        mandatory=True)
    }

    parameter_overrides = {
        'target': Override(settable=True),

    }

    valuetype = float
    _driveTarget = None

    def doStart(self, value):
        # I have to use my private _driveTarget as the target
        # attribute is marked volatile in EpicsMoveable and is
        # not holding the real target.
        self._driveTarget = value
        EpicsMoveable.doStart(self, value)

    def doStatus(self, maxage=0):
        pos = self.doRead(0)
        if self._driveTarget:
            if abs(pos - self._driveTarget) < self.window:
                self._driveTarget = None
                return status.OK, 'Done'
            else:
                return status.BUSY, 'Moving'
        return status.OK, 'Done'


class EpicsArrayReadable(EpicsReadable):
    parameters = {
        'count': Param('How many array values to read',
                       type=int, mandatory=True),
    }

    def doRead(self, maxage=0):
        if epics.ca.current_context() is None:
            epics.ca.use_initial_context()
        result = self._pvs['readpv'].get(timeout=self.epicstimeout,
                                         count=self.count)
        if result is None:  # timeout
            raise CommunicationError(self, 'timed out getting PV %r from EPICS'
                                     % self._get_pv_name('readpv'))
        return result

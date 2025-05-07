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
from nicos.core import Attach, HasPrecision, Moveable, Param, floatrange
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep


class A6Motor(HasPrecision, BaseSequencer):
    """
    A6 at EIGER has to wait for the shielding blocks to be moved.
    The plan was to check for this in the SPS, but this feature never
    materialized. Thus, we just wait for wait_period seconds after the motor
    finished. This is implemented in this class.
    """

    parameters = {
        'wait_period': Param('Waiting time after the motor finished',
                             type=floatrange(0), default=7),
    }

    attached_devices = {
        'raw_motor': Attach('The real motor to drive',
                            Moveable),
    }

    def doRead(self, maxage=0):
        return self._attached_raw_motor.read(maxage)

    def doStart(self, target):
        self.reset()
        BaseSequencer.doStart(self, target)

    def _generateSequence(self, target):
        return [
            SeqDev(self._attached_raw_motor, target),
            SeqSleep(self.wait_period)
        ]

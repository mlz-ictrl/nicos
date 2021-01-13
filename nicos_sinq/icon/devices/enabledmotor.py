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
#   Pierre Boillat <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.core import Attach, Readable
from nicos.core.errors import NicosError
from nicos.core.status import BUSY

from nicos_ess.devices.epics.motor import EpicsMotor, HomingProtectedEpicsMotor

# pylint: disable=no-else-raise


class EnabledMotor(HomingProtectedEpicsMotor):
    """
    At ICON there are motors which are only allowed to run
    while a door a is closed. This is indicated by a
    Digital I/O. This is implemented in this module.
    """

    attached_devices = {
        'lock': Attach('I/O to consult if the motor is allowed to run or not',
                       Readable),
    }

    _stop_sent = False

    def doStart(self, pos):
        if self._attached_lock.read(0) == 0:
            raise NicosError(self, 'Motor cannot move while door is open')
        self._stop_sent = False
        EpicsMotor.doStart(self, pos)

    def doStatus(self, maxage=0):
        ret = EpicsMotor.doStatus(self, maxage)
        if ret[0] == BUSY:
            if self._attached_lock.read(0) == 0 and not self._stop_sent:
                self.stop()
                session.log.error('Door opened, stopping motor')
                self._stop_sent = True
        return EpicsMotor.doStatus(self, maxage)

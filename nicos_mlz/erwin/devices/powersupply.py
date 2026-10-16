# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Definition special power supply class for CHARM detector."""

from time import monotonic

from tango import DevState

from nicos import session
from nicos.core import status
from nicos.core.constants import MAINTENANCE, MASTER
from nicos.core.utils import statusString
from nicos.devices.entangle import PowerSupply
from nicos.devices.tango import PyTangoMixin


class HVPowerSupply(PowerSupply):

    def _combinedStatus(self, maxage=0):
        """Create a combined status from doStatus, isAtTarget and timedOut

        If a timeout happens, use the status set by self.timeout_status and
        call `timeoutAction` once if defined. Pollers and other `SLAVE`s do
        *not* call `timeoutAction`.
        """
        from nicos.core.device import Readable  # isort:skip
        code, msg = Readable._combinedStatus(self, maxage)

        if code == status.OK and self._timeoutTime:
            if not self.isAtTarget(self.read(maxage)):
                code = status.BUSY
                msg = statusString('target not yet reached', msg)
            else:
                self._targetReached()
        if code == status.BUSY:
            if self.isTimedOut():
                code = self.timeout_status
                msg = statusString('movement timed out', msg)
                # only call once per timeout, flag is reset in Device.start()
                if not self._timeoutActionCalled and \
                        session.mode in (MASTER, MAINTENANCE):
                    try:
                        if hasattr(self, 'timeoutAction'):
                            self.timeoutAction()
                            self._timeoutActionCalled = True
                            return self._combinedStatus(maxage)
                    except Exception:
                        self.log.exception('error calling timeout action',
                                           exc=True)
                    finally:
                        self._timeoutActionCalled = True
            elif self._timesout:
                # give indication about the phase of the movement
                for m, t in self._timesout or []:
                    if t > monotonic():
                        msg = statusString(m, msg)
                        break
        elif code == status.ERROR:
            self._timeoutActionCalled = True
        elif code == status.WARN:
            self._clearTimeout()
        return (code, msg)

    def doReset(self):
        self.log.debug('disable: %s', self)
        self.disable()
        while self._dev.State() == DevState.MOVING:
            session.delay(self._base_loop_delay)
        self.log.debug('reset: %s', self)
        PyTangoMixin.doReset(self)
        while self._dev.State() == (DevState.MOVING, DevState.INIT):
            session.delay(self._base_loop_delay)

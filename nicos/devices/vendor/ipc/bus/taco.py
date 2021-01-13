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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""IPC (Institut für Physikalische Chemie, Göttingen) hardware classes."""

from IO import StringIO  # pylint: disable=import-error
from RS485Client import RS485Client  # pylint: disable=import-error
from TACOClient import TACOError  # pylint: disable=import-error

from nicos import session
from nicos.core import CommunicationError, Param, ProgrammingError, floatrange
from nicos.devices.taco.core import TacoDevice

from .base import ACK, DC1, DC2, DC3, EOT, NAK, InvalidCommandError, \
    IPCModBus, IPCModBusRS232


class IPCModBusTaco(TacoDevice, IPCModBus):
    """IPC protocol communication over TACO RS-485 server."""

    taco_class = RS485Client
    taco_errorcodes = {
        4019: InvalidCommandError,
        537133063: InvalidCommandError,
    }

    parameters = {
        'bustimeout': Param('Communication timeout for this device',
                            type=floatrange(0.1, 1200), default=0.5,
                            settable=True),
    }

    def send(self, addr, cmd, param=0, length=0):
        return self._taco_guard(self._dev.SDARaw, addr, cmd, length, param)

    def get(self, addr, cmd, param=0, length=0):
        return self._taco_guard(self._dev.SRDRaw, addr, cmd, length, param)

    def ping(self, addr):
        return self._taco_guard(self._dev.Ping, addr)

    def doReadBustimeout(self):
        if self._dev and hasattr(self._dev, 'timeout'):
            return float(self._taco_guard(self._dev.timeout))
        raise ProgrammingError(self, "TacoDevice has no 'timeout'!")

    def doUpdateBustimeout(self, value):
        if not self._sim_intercept and self._dev:
            try:
                self._taco_update_resource('timeout', str(value))
            except (TACOError, Exception) as e:
                self.log.warning('ignoring %r', e)


class IPCModBusTacoSerial(TacoDevice, IPCModBusRS232):
    taco_class = StringIO

    def _transmit(self, request, retlen, last_try=False):
        response = ''
        self._dev.write(request)
        for _i in range(self.comtries):
            session.delay(self.bustimeout)
            try:
                data = self._dev.read()
            except Exception:
                data = ''
            if not data:
                continue
            response += data
            if response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                return response
        raise CommunicationError(self, 'no response')

    def doReset(self):
        TacoDevice.doReset(self)

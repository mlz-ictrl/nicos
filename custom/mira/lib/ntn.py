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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""FUG NTN14000m power supply special class."""

import time

from IO import StringIO

from nicos.core import status, Moveable, HasLimits, Override, NicosError, Param
from nicos.devices.taco.core import TacoDevice
from nicos.core import MASTER


class FUG(TacoDevice, HasLimits, Moveable):
    """
    Device object for a FUG NTN14000m power supply.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='A'),
    }

    parameters = {
        'voltage':    Param('Maximum voltage', default=100),
        'variance':   Param('Max difference of read and set value', default=0.05),
        'readoffset': Param('Offset for read value', settable=True),
        'readslope':  Param('Slope for read value', settable=True, default=1),
    }

    def _ask(self, what):
        # setting "what to ask" and asking are two different things; but we have to
        # combine them to keep atomicity of communicate; in order to keep the
        # supply happy about the rapid succession, a few spaces are needed as below
        return self._taco_guard(self._dev.communicate, what + '\r' + ' '*24 + '?')

    def doInit(self, mode):
        maxcur = self._ask('N4')
        assert float(maxcur) > 50
        if self.abslimits[1] > maxcur:
            raise NicosError(self, 'absolute maximum bigger than device maximum')
        if mode == MASTER:
            self.doReset()

    def doReadVoltage(self):
        maxvolt = self._ask('N3')
        return float(maxvolt)

    def doWriteVoltage(self, value):
        self._taco_guard(self._dev.writeLine, 'U%f' % value)

    def doReset(self):
        # deactivate "execute on X" mode
        self._taco_guard(self._dev.writeLine, 'G0;X')

    def doRead(self, maxage=0):
        cval = float(self._ask('N1')[:-2])
        return self.readslope * cval + self.readoffset

    def doStatus(self, maxage=0):
        sval = self._ask('N0')
        if sval[2] == '0':
            return status.ERROR, 'supply is switched off'
        return status.OK, 'idle'

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'I%f' % value)
        time.sleep(0.5)
        if abs(self.doRead() - value) > value*self.variance + 0.2:
            self.log.warning('failed to set new current of %.3f A; re-setting '
                             'voltage limit to %.1f V and trying again' %
                             (value, self.voltage))
            # first set nominal current to zero
            self._taco_guard(self._dev.writeLine, 'I0')
            # then set maximum voltage
            self._taco_guard(self._dev.writeLine, 'U%f' % self.voltage)
            # now set desired current
            self._taco_guard(self._dev.writeLine, 'I%f' % value)
            time.sleep(0.5)
            if abs(self.doRead() - value) > value*self.variance + 0.2:
                raise NicosError(self, 'power supply failed to set current value')

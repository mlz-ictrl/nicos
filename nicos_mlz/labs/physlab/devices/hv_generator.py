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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Attach, Moveable, status
from nicos.core.params import Param, floatrange, tupleof
from nicos.devices.entangle import PyTangoDevice
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod, \
    SeqSleep


class HighVoltagePowerSupply(PyTangoDevice, BaseSequencer):

    attached_devices = {
        'voltage': Attach('Voltage channel of the xray generator', Moveable),
        'current': Attach('Current channel of the xray generator', Moveable),
    }

    parameters = {
        'waterflow': Param('waterflow of the cooling water',
                           type=float, settable=False, unit='l/min',
                           volatile=True),
        'heatercurrent': Param('heater current of the x-ray tube',
                               type=float, settable=False, unit='A',
                               volatile=True),
        'ramp': Param('ramp of the current and voltage',
                      type=float, settable=True, unit='unit/min'),
        'switchdelay': Param('time to switch between voltage and current '
                             'ramping, is needed to avoid cooling water '
                             'switching off',
                             type=floatrange(1, 300), default=60, unit='s',
                             userparam=False, settable=True,),
    }

    valuetype = tupleof(float, float)
    hardware_access = True

    def doRead(self, maxage=0):
        return (self._attached_voltage.read(maxage),
                self._attached_current.read(maxage))

    def doReadWaterflow(self):
        return self._dev.waterflow

    def doReadHeatercurrent(self):
        return self._dev.heatercurrent

    def doReadRamp(self):
        return self._attached_voltage.ramp

    def doWriteRamp(self, ramp):
        self._attached_voltage.ramp = ramp
        self._attached_current.ramp = ramp

    def _generateSequence(self, target):
        if self.isAtTarget(target=target):
            return []
        voltage, current = target
        vchannel = self._attached_voltage
        cchannel = self._attached_current

        if voltage < 1 or current < 1:
            return self._vcseq(20.0, 5.0) + self._onseq(False)

        if vchannel.voltage < 1 or cchannel.current < 1:
            return self._onseq(True) + [SeqSleep(5)] + self._vcseq(voltage,
                                                                   current)

        return self._vcseq(voltage, current)

    def _vcseq(self, voltage, current):
        vchannel = self._attached_voltage
        cchannel = self._attached_current

        seq = [SeqDev(vchannel, voltage), SeqDev(cchannel, current)]

        if cchannel.current > current:
            return seq[::-1]
        else:
            seq.insert(1, SeqSleep(self.switchdelay))
        return seq

    def _onseq(self, on):
        vps, cps = self._attached_voltage, self._attached_current
        return [SeqMethod(vps, 'doEnable', on), SeqMethod(cps, 'doEnable', on)]

    def doPoll(self, n, maxage):
        self._pollParam('heatercurrent', 1)
        self._pollParam('waterflow', 1)

    def doStatus(self, maxage=0):
        st = BaseSequencer.doStatus(self, maxage)
        if st[0] != status.OK:
            return st
        return PyTangoDevice.doStatus(self, maxage)

    def doReset(self):
        BaseSequencer.doReset(self)
        PyTangoDevice.doReset(self)

    def doIsAtTarget(self, pos, target):
        return pos == target

    def doTime(self, old_value, target):
        return sum(dev.doTime(ov, t) for (dev, ov, t) in
                   zip((self._attached_voltage, self._attached_current),
                       old_value, target)) + self.switchdelay

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Attach, Override, Param, Readable, SLAVE, status
from nicos.devices.abstract import TransformedReadable
from nicos.devices.generic import VirtualMotor
from nicos.utils.functioncurves import Curves
from nicos_jcns.moke01.devices.moke import MokeMagnet


class VirtualMokeMagnet(MokeMagnet):

    parameter_overrides = {
        'ramp': Override(prefercache=False,),
        'maxramp': Override(prefercache=False,),
    }


class VirtualMokeSensor(TransformedReadable):
    """The sensor class that transforms current value of the attached device
    through its own valuemap.
    It features ``increasing`` parameter to indicate if its new value is higher
    than the previous one to account for hysteresis.
    """

    attached_devices = {
        'mappeddevice': Attach(
            'Attached device that produces values to map to values of this device',
            Readable
        ),
    }

    parameters = {
        'increasing': Param(
            'Indicates if the sensor is going towards higher values',
            type=bool, settable=True, internal=True, default=True,
        ),
        'valuemap': Param(
            'Magnetic field fitting curves',
            type=Curves, settable=True, default=Curves(),
        ),
        'error': Param(
            'Relative error of measurement',
            type=float, settable=True, default=0.05,
        ),
    }

    def doInit(self, mode):
        self._mappeddevice = self._attached_mappeddevice

    def _mapReadValue(self, value):
        if self._mode != SLAVE:
            self.increasing = self._mappeddevice.increasing
        if self.increasing:
            return self.valuemap.increasing()[0].yvx(value).y.n
        return self.valuemap.decreasing()[0].yvx(value).y.n

    def _readRaw(self, maxage=0):
        return self._mappeddevice.read(maxage)

    def readStd(self, value):
        return abs(value) * self.error


class VirtualPowerSupply(VirtualMotor):
    """A virtual power supply.
    It features ``increasing`` parameter to indicate if the new value of
    electric current is higher than the previous value to account for
    hysteresis.
    """

    parameters = {
        'increasing': Param(
            'Indicates if the PS is ramping towards higher values',
            type=bool, settable=True, internal=True, default=True,
        ),
        'maxramp': Param(
            'Maximal ramp value',
            unit='A/min', type=float, mandatory=True
        ),
    }

    parameter_overrides = {
        'speed': Override(type=float),
        'ramp': Override(type=float, prefercache=False, no_sim_restore=False),
    }

    def doStart(self, target):
        self.increasing = target >= self.curvalue
        if self.status(0)[0] == status.DISABLED:
            self.enable()
            self._hw_wait()
        VirtualMotor.doStart(self, target)

    def doEnable(self, on):
        if not on:
            self.ramp = self.maxramp
            VirtualMotor.start(self, 0)
            self._hw_wait()
        VirtualMotor.doEnable(self, on)

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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************


from nicos.core import CanDisable, Override, Param
from nicos.devices.entangle import SpectrumInput


class Spectrometer(CanDisable, SpectrumInput):

    parameter_overrides = {
        'xticks': Override(volatile=True, unit='nm'),
    }

    parameters = {
        'averages': Param(
            'Number of scans to average over.',
            type=int, settable=True, unit='', category='general',
        ),
        'integration_time': Param(
            'Integration time (exposure duration).',
            type=float, settable=True, unit='', category='general',
        ),
    }

    def doEnable(self, on):
        if on:
            self._dev.On()
        else:
            self._dev.Off()

    def doReadAverages(self):
        return self._dev.averages

    def doWriteAverages(self, value):
        self._dev.averages = value

    def doReadIntegration_Time(self):
        return self._dev.integrationTime

    def doWriteIntegration_Time(self, value):
        self._dev.integrationTime = value


class HR4000(Spectrometer):

    parameter_overrides = {
        'integration_time': Override(unit='usec'),
    }


class AV4096(Spectrometer):

    parameter_overrides = {
        'integration_time': Override(unit='ms'),
    }

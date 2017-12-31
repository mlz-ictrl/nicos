#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Allow changing a few burst properties of the agilent funcgens used for tisane
"""

from nicos.core import Param, Override, floatrange, oneof, intrange
from nicos.devices.tango import NamedDigitalOutput


class Burst(NamedDigitalOutput):
    parameters = {
        'frequency': Param('Frequency of the signal.', unit='Hz',
                           type=floatrange(2e-3, 1e7), settable=True,
                           category='experiment'),
        'amplitude': Param('Amplitude (V_PP) of the signal.', unit='V',
                           type=floatrange(1e-3, 10), settable=True,
                           category='experiment'),
        'offset':    Param('Offset of the signal.', unit='V',
                           type=floatrange(-10, 10), settable=True,
                           category='experiment'),
        'shape':     Param('Shape of the signal.', settable=True,
                           type=oneof('sin', 'square', 'ramp'),
                           category='experiment'),
        'duty':      Param('Dutycycle for square, assymetry for ramp.',
                           type=intrange(0, 100), unit='%', settable=True,
                           category='experiment'),

    }
    parameter_overrides = {
        'mapping': Override(mandatory=False, default=dict(On=1, Off=0)),
    }

    def doReadFrequency(self):
        return float(self._getProperty('frequency'))

    def doWriteFrequency(self, value):
        self._dev.SetProperties(['frequency', '%.8f' % value])
        return self.doReadFrequency()

    def doReadAmplitude(self):
        return float(self._getProperty('amplitude'))

    def doWriteAmplitude(self, value):
        self._dev.SetProperties(['amplitude', '%.8f' % value])
        return self.doReadAmplitude()

    def doReadOffset(self):
        return float(self._getProperty('offset'))

    def doWriteOffset(self, value):
        self._dev.SetProperties(['offset', '%.8f' % value])
        return self.doReadOffset()

    def doReadDutycycle(self):
        if self.shape == 'square':
            return float(self._getProperty('dutycycle'))
        elif self.shape == 'ramp':
            return float(self._getProperty('symmetry'))
        else:
            return 50.0

    def doWriteDutycycle(self, value):
        if self.shape == 'square':
            if not 0 <= value <= 100:
                raise ValueError('Dutycycle must be between 0..100%!')
            self._dev.SetProperties(['dutycycle', '%.8f' % value])
        elif self.shape == 'ramp':
            if not 10 <= value <= 90:
                raise ValueError('Dutycycle must be between 10..90%!')
            self._dev.SetProperties(['symmetry', '%.8f' % value])
        return self.doReadDutycycle()

    def doReadShape(self):
        return self._getProperty('shape')

    def doWriteShape(self, value):
        self._dev.SetProperties(['shape', '%s' % value])
        return self.doReadShape()

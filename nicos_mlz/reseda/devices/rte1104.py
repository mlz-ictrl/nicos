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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Devices accessing the Rohde & Schwarz oscillosope RTE1104"""

import math

from nicos.core import Attach, Moveable, Override, Param, Readable, intrange, \
    status
from nicos.devices.entangle import StringIO


class RTE1104(Readable):

    parameters = {
        'channel': Param('calculation channel',
                         type=intrange(1, 8), settable=False,
                         default=1),
        'timescale': Param('Time scale setting',
                           type=float, settable=True, userparam=True,
                           volatile=True, category='general'),
        'yscale': Param('Y axis scaling',
                        type=float, settable=True, userparam=True,
                        volatile=True, category='general'),
    }

    attached_devices = {
       'io': Attach('Communication device', StringIO),
    }

    def doRead(self, maxage=0):
        return float(self._attached_io.communicate('MEAS%d:ARES?' %
                                                   self.channel))

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doReadTimescale(self):
        return float(self._attached_io.communicate('TIM:SCAL?'))

    def doWriteTimescale(self, value):
        self._attached_io.writeLine('TIM:SCAL %g' % value)

    def doReadYscale(self):
        return float(self._attached_io.communicate('CHAN%d:SCAL?' %
                                                   self.channel))

    def doWriteYscale(self, value):
        self._attached_io.writeLine('CHAN%d:SCAL %g' %
                                    (self.channel, value))


class RTE1104TimescaleSetting(Moveable):

    attached_devices = {
        'io': Attach('Communication device', StringIO),
        'freqgen': Attach('frequency generator', Moveable, optional=True),
    }

    parameters = {
        'timescale': Param('Time scale setting',
                           type=float, settable=False, userparam=False,
                           default=10., category='general'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='Hz'),
    }

    valuetype = float

    def doRead(self, maxage=0):
        # main value is freq!
        if self._attached_freqgen:
            return self._attached_freqgen.read(maxage)
        return self.timescale/float(self._attached_io.communicate(
            'TIM:SCAL?' % self.channel))

    def doStart(self, target):
        self._attached_io.writeLine('TIM:SCAL %g' %
                                    (self.timescale/float(target)))
        if self._attached_freqgen:
            self._attached_freqgen.start(target)

    def doStatus(self, maxage=0):
        if self._attached_freqgen:
            return self._attached_freqgen.status(maxage)
        return status.OK, ''


class RTE1104YScaleSetting(Moveable):

    parameters = {
        'channel': Param('Input channel',
                         type=intrange(1, 4), settable=False,
                         default=1),
    }

    attached_devices = {
       'io': Attach('Communication device', StringIO),
       'regulator': Attach('regulator for the amplitude', Moveable,
                           optional=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True),
    }

    valuetype = float

    def doReadUnit(self):
        if self._attached_regulator:
            return self._attached_regulator.unit
        return 'V'

    def doRead(self, maxage=0):
        # main value is target amplitude
        if self._attached_regulator:
            return self._attached_regulator.read(maxage)
        setting = float(self._attached_io.communicate('CHAN%d:SCAL?' %
                                                      self.channel))
        return setting * 10. / (2.2 * math.sqrt(2))

    def doStart(self, value):
        setting = math.ceil(value * math.sqrt(2.) * 2.2) / 10.
        self._attached_io.writeLine('CHAN%d:SCAL %g' %
                                    (self.channel, setting))
        if self._attached_regulator:
            self._attached_regulator.start(value)

    def doStatus(self, maxage=0):
        if self._attached_regulator:
            return self._attached_regulator.status(maxage)
        return status.OK, ''

    def doStop(self):
        if self._attached_regulator:
            self._attached_regulator.stop()

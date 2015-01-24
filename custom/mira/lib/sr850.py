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

"""Class for Stanford Research SR850 lock-in amplifier."""

from math import hypot, atan2, degrees
from time import time

from IO import StringIO

from nicos.core import intrange, Measurable, Param, Value, CommunicationError, \
    ConfigurationError, NicosError
from nicos.devices.taco.core import TacoDevice
from nicos.core import SIMULATION


TIMECONSTANTS = sum(([k, 3*k] for k in range(1, 11)), [])


class Amplifier(TacoDevice, Measurable):
    """
    Stanford Research SR850 lock-in amplifier.
    """

    parameters = {
        'frequency': Param('Reference freqency', unit='Hz', settable=True,
                           category='general'),
        'amplitude': Param('Reference sine amplitude', unit='Vrms',
                           settable=True, category='general'),
        'phase':     Param('Phase shift', unit='deg',
                           settable=True, category='general'),
        'harmonic':  Param('Number of harmonic to detect', type=int,
                           settable=True, category='general'),
        'timeconstant': Param('Time constant of the low pass filter', type=int,
                              settable=True, category='general', unit='us'),
        'reserve':      Param('Dynamic reserve', type=intrange(0, 5),
                              settable=True, category='general'),
        'measurements': Param('Number of measurements to average over',
                              type=int, default=100, settable=True),
    }

    taco_class = StringIO

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        reply = self._taco_guard(self._dev.communicate, '*IDN?')
        if not reply.startswith('Stanford_Research_Systems,SR8'):
            raise CommunicationError('wrong identification: %r' % reply)

    def valueInfo(self):
        return Value('X', unit='V', fmtstr=self.fmtstr), \
               Value('Y', unit='V', fmtstr=self.fmtstr), \
               Value('R', unit='V', fmtstr=self.fmtstr), \
               Value('Theta', unit='deg', type='counter', fmtstr=self.fmtstr)

    def doSetPreset(self, **preset):
        self._delay = preset.get('delay', 0)

    def doStart(self):
        self._started = time()

    def doIsCompleted(self):
        return (time() > self._started + self._delay)

    def doRead(self, maxage=0):
        xs, ys = [], []
        N = self.measurements
        for _ in range(N):
            try:
                newx = float(self._taco_guard(self._dev.communicate, 'OUTP? 1'))
                newy = float(self._taco_guard(self._dev.communicate, 'OUTP? 2'))
            except (NicosError, ValueError):
                newx = float(self._taco_guard(self._dev.communicate, 'OUTP? 1'))
                newy = float(self._taco_guard(self._dev.communicate, 'OUTP? 2'))
            xs.append(newx)
            ys.append(newy)
        X = sum(xs) / float(N)
        Y = sum(ys) / float(N)
        R = hypot(X, Y)
        Theta = degrees(atan2(Y, X))
        return [X, Y, R, Theta]

    def doStop(self):
        pass

    def doReadFrequency(self):
        return float(self._taco_guard(self._dev.communicate, 'FREQ?'))

    def doWriteFrequency(self, value):
        self._taco_guard(self._dev.writeLine, 'FREQ %f' % value)
        if self.doReadFrequency() != value:
            raise NicosError(self, 'setting new frequency failed')

    def doReadAmplitude(self):
        return float(self._taco_guard(self._dev.communicate, 'SLVL?'))

    def doWriteAmplitude(self, value):
        self._taco_guard(self._dev.writeLine, 'SLVL %f' % value)
        if self.doReadAmplitude() != value:
            raise NicosError(self, 'setting new amplitude failed')

    def doReadPhase(self):
        return float(self._taco_guard(self._dev.communicate, 'PHAS?'))

    def doWritePhase(self, value):
        self._taco_guard(self._dev.writeLine, 'PHAS %f' % value)
        if self.doReadPhase() != value:
            raise NicosError(self, 'setting new phase failed')

    def doReadHarmonic(self):
        return int(self._taco_guard(self._dev.communicate, 'HARM?'))

    def doWriteHarmonic(self, value):
        self._taco_guard(self._dev.writeLine, 'HARM %d' % value)
        if self.doReadHarmonic() != value:
            raise NicosError(self, 'setting new harmonic failed')

    def doReadTimeconstant(self):
        value = int(self._taco_guard(self._dev.communicate, 'OFLT?'))
        return TIMECONSTANTS[value]

    def doWriteTimeconstant(self, value):
        if value not in TIMECONSTANTS:
            raise ConfigurationError(self, 'invalid time constant, valid ones '
                                     'are ' + ', '.join(map(str, TIMECONSTANTS)))
        value = TIMECONSTANTS.index(value)
        self._taco_guard(self._dev.writeLine, 'OFLT %d' % value)
        if self.doReadTimeconstant() != value:
            raise NicosError(self, 'setting new time constant failed')

    def doReadReserve(self):
        return int(self._taco_guard(self._dev.communicate, 'RSRV?'))

    def doWriteReserve(self, value):
        self._taco_guard(self._dev.writeLine, 'RSRV %d' % value)
        if self.doReadReserve() != value:
            raise NicosError(self, 'setting new reserve failed')

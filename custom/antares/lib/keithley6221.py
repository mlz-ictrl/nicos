#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Class for Keithley 6221 constant current source."""

from IO import StringIO

from nicos.core import CommunicationError, status, Moveable, HasLimits, \
    SIMULATION
from nicos.devices.taco.core import TacoDevice


class Current(TacoDevice, HasLimits, Moveable):
    """
    Current amplitude.
    """

    taco_class = StringIO

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        reply = self._taco_guard(self._dev.communicate, '*IDN?')
        if not reply.startswith('KEITHLEY'):
            raise CommunicationError('wrong identification: %r' % reply)

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'SOUR:WAVE:AMPL %f' % value)
        self._taco_guard(self._dev.writeLine, 'SOUR:WAVE:OFFS 0')
        self._taco_guard(self._dev.writeLine, 'SOUR:WAVE:ARM')
        self._taco_guard(self._dev.writeLine, 'SOUR:WAVE:INIT')

    def doRead(self, maxage=0):
        return float(self._taco_guard(self._dev.communicate, 'SOUR:WAVE:AMPL?'))

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doStop(self):
        pass


class Frequency(TacoDevice, HasLimits, Moveable):
    """
    Current frequency.
    """

    taco_class = StringIO

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        reply = self._taco_guard(self._dev.communicate, '*IDN?')
        if not reply.startswith('KEITHLEY'):
            raise CommunicationError('wrong identification: %r' % reply)

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'SOUR:WAVE:FREQ %f' % value)

    def doRead(self, maxage=0):
        return float(self._taco_guard(self._dev.communicate, 'SOUR:WAVE:FREQ?'))

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doStop(self):
        pass

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

"""Heinzinger device."""

import time

from IO import StringIO

from nicos.core import status, Moveable, HasLimits, Override, NicosError, Param, \
    CommunicationError
from nicos.devices.taco.core import TacoDevice
from nicos.core import MASTER


class Heinzinger(TacoDevice, HasLimits, Moveable):
    """
    Device object for a Heinzinger PTN3p power supply.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit': Override(mandatory=False, default='A'),
    }

    parameters = {
        'variance': Param('Max difference of real and set value',
                          default=0.05),
    }

    def doInit(self, mode):
        idn = self._taco_guard(self._dev.communicate, '*IDN?')
        if not idn.startswith('test_PTN'):
            raise CommunicationError(self, 'strange model for PTN3p: %r' % idn)
        maxcur, _maxvolt = map(float, idn[8:].split('-'))
        if maxcur < self.abslimits[1]:
            raise NicosError(self, 'absolute maximum bigger than device maximum')
        if mode == MASTER:
            self.doReset()
        self._calibvalue = float(self._taco_guard(self._dev.communicate,
                                                  'CAL:CURR?'))

    def doReset(self):
        self._taco_guard(self._dev.writeLine, 'CAL:CURR 80')
        time.sleep(0.2)
        self._taco_guard(self._dev.writeLine, 'CAL:VOLT 80')
        time.sleep(0.2)

    def doRead(self, maxage=0):
        cval = float(self._taco_guard(self._dev.communicate,
                                      'MEASURE:CURRENT?'))
        return cval * 80. / self._calibvalue

    def doStatus(self, maxage=0):
        sval = self._taco_guard(self._dev.communicate, 'OUTP:STATE?')
        if sval == '0':
            return status.OK, 'idle'
        return status.ERROR, 'status code: %s' % sval

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'CURR %f' % value)
        time.sleep(1.5)
        newval = self.read(0)
        if abs(newval - value) > value*self.variance + 0.2:
            self.log.warning('failed to set new current of %.3f A ('
                             'readout %.3f A); trying again' % (value, newval))
            # first set nominal current to zero
            self._taco_guard(self._dev.writeLine, 'CURR 0')
            time.sleep(2)
            # now set desired current
            self._taco_guard(self._dev.writeLine, 'CURR %f' % value)
            time.sleep(1.5)
            if abs(self.doRead() - value) > value * self.variance + 0.2:
                raise NicosError(self, 'power supply failed to set current value')


class HeinzingerViaHPE(TacoDevice, HasLimits, Moveable):
    """
    Device object for a Heinzinger PTN3p power supply via external input
    HPE3631.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='A'),
    }

    parameters = {
        'scale': Param('Scale factor A_out/V_in', type=float, mandatory=True),
    }

    def doInit(self, mode):
        idn = self._taco_guard(self._dev.communicate, '*IDN?')
        if 'HEWLETT-PACKARD' not in idn:
            raise CommunicationError(self, 'strange model for HPE: %r' % idn)

    def doRead(self, maxage=0):
        self._taco_guard(self._dev.writeLine, 'INSTRUMENT:NSELECT 2')
        time.sleep(1)
        try:
            return float(self._taco_guard(self._dev.communicate, 'VOLT?')) * \
                self.scale
        except Exception:
            self.log.warning('read failed, trying again')
            time.sleep(5)
            return float(self._taco_guard(self._dev.communicate, 'VOLT?')) * \
                self.scale

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'INSTRUMENT:NSELECT 2')
        time.sleep(1)
        self._taco_guard(self._dev.writeLine, 'VOLT %f' % (value / self.scale))


class HPECurrent(TacoDevice, HasLimits, Moveable):
    """
    Device object for HPE 3633 current control.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='A'),
    }

    parameters = {
    }

    def doInit(self, mode):
        idn = self._taco_guard(self._dev.communicate, '*IDN?')
        if 'HEWLETT-PACKARD' not in idn:
            raise CommunicationError(self, 'strange model for HPE: %r' % idn)

    def doRead(self, maxage=0):
        try:
            return float(self._taco_guard(self._dev.communicate, 'MEAS:CURR?'))
        except Exception:
            self.log.warning('read failed, trying again')
            time.sleep(3)
            try:
                return float(self._taco_guard(self._dev.communicate,
                                              'MEAS:CURR?'))
            except Exception:
                self.log.warning('read failed, trying again')
                time.sleep(5)
                return float(self._taco_guard(self._dev.communicate,
                                              'MEAS:CURR?'))

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

    def doStart(self, value):
        self._taco_guard(self._dev.writeLine, 'CURR %f' % value)

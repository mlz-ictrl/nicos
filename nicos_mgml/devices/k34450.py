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
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Allows to measure in voltage on Keysight 34450A"""

import time

from nicos.core import Attach, Device, Measurable, Override, Param, Readable, \
    Value, oneof, status
from nicos.devices.entangle import StringIO


class BaseK34450(Device):

    attached_devices = {
        'k34450': Attach('Keysight k34450A multimeter', StringIO,
                         optional=True),
    }

    _canCurrent = False
    _measuring = False

    def comm(self, cmd, response=False):
        self.log.debug('comm: %r', cmd)
        if response:
            resp = self._attached_k34450.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_k34450.writeLine(cmd)
        time.sleep(0.01)
        return None

    def doInit(self, mode):
        self.doReset()
        self.log.debug('init complete')

    def doReset(self):
        # reset device
        self.comm('*CLS;SYST:PRES')
        time.sleep(0.1)
        # set readout with units
        self.comm('FORM:OUTP 2')


class MultiReader(BaseK34450, Readable):

    parameters = {
        'unit': Param('Unit',
                      type=oneof('V', 'A', 'Ohm', 'Hz', 'F', 'C'), settable=False,
                      default='V',),
        'type': Param('Type of measurement',
                      type=oneof('VOLTage:AC', 'VOLTage:DC', 'CURRent:AC',
                                 'CURRent:DC', 'DIODe', 'FREQuency',
                                 'RESistance', 'FRESistance', 'TEMPerature',
                                 'CONTinuity', 'CAPacitance'), settable=True,
                      default='VOLTage:DC',),
        'resolution': Param('Resolution of the measurement',
                            type=oneof('SLOW', 'MEDium', 'FAST', 'DEF'),
                            settable=True, default='DEF',),
        'range': Param('Ranging of the measurement',
                       type=oneof('AUTO', 'MIN', 'MAX'), settable=True,
                       default='AUTO',),
    }

    parameter_overrides = {
        'pollinterval': Override(default=2),
        'maxage':       Override(default=5),
    }

    _value = 0
    _measuring = False

    def doWriteType(self, value):
        self.comm(f'CONF:{value} {self.range},{self.resolution}')

    def doWriteResolution(self, value):
        self.comm(f'CONF:{self.type} {self.range},{value}')

    def doWriteRange(self, value):
        if value == 'AUTO':
            self.resolution = 'DEF'
        self.comm(f'CONF:{self.type} {value},{self.resolution}')

    def doReset(self):
        BaseK34450.doReset(self)
        # reset device
        self.comm(f'CONF:{self.type} {self.range},{self.resolution}')
        self._measuring = False
        time.sleep(0.1)

    def getValueInUnits(self, resp):
        v, u = resp.split(' ')
        conversion = {
            'VDC': 'V',
            'VAC': 'V',
            'ADC': 'A',
            'AAC': 'A',
            'OHMS': 'Ohm',
            'HZ': 'Hz',
            'F': 'F',
            'C': 'C',
        }
        self._setROParam('unit', conversion.get(u, ''))
        return float(v)

    def doRead(self, maxage=0):
        self._measuring = True
        resp = ''
        while resp == '':
            resp = self.comm('READ?', True)
            time.sleep(0.05)
        self._measuring = False
        return self.getValueInUnits(resp)

    def doStatus(self, maxage=0):
        if self._measuring:
            return (status.BUSY, 'measuring')
        return (status.OK, 'idle')


class Multimeter(MultiReader, Measurable):

    def doStart(self):
        self.log.debug('asked doStart')
        self._measuring = True
        resp = ''
        while resp == '':
            resp = self.comm('READ?', True)
            time.sleep(0.05)
        self._value = self.getValueInUnits(resp)
        self._measuring = False

    def doSetPreset(self, **preset):
        # do nothing, no preset
        pass

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        return self._value

    def valueInfo(self):
        """Return current value information"""
        return Value(self.type, unit=self.unit, fmtstr=self.fmtstr),

    def doFinish(self):
        pass

    def doStop(self):
        pass

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Jens Krueger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Class for Oxford magnet consisting of the Mercury iPS power supply
"""

__version__ = "$Revision$"

# from PowerSupply import CurrentControl
from IO import StringIO

from nicos.core import Moveable, HasLimits, Param, Override, waitForStatus, \
     floatrange, status, oneof, Device, CommunicationError, InvalidValueError
from nicos.devices.taco.core import TacoDevice

class OxfordMercury(HasLimits, TacoDevice, Moveable):
    """Class for the readout of a Mcc2-coder"""

    taco_class = StringIO

    parameter_overrides = {
        'unit':       Override(type=oneof('A', 'T'), default='A', settable=False),
    }

    parameters = {
        'ramp':       Param('Rate of ramping', type=floatrange(0, 2),
                            default=1.8, unit='main/min', settable=True),
        'ramplimit' : Param('maximum ramp', type=float,
                            unit='main/min', settable=False),
        'scale':      Param('conversion factor from T to A', type=float,
                            default=31.280, unit='', settable=False),
    }

    def doInit(self, mode):
        if mode != 'simulation':
            if not self._dev.communicate('*IDN?').startswith('IDN'):
                raise CommunicationError(self, 'No Response from Mercury iPS,'
                                               ' please check!')

    def doStart(self, value):
        self.doStop()
        if self.unit == 'A':
            self._write('DEV:GRPZ:PSU:SIG:CSET:%f' % float(value))
        else:
            self._write('DEV:GRPZ:PSU:SIG:FSET:%f' % float(value))
        self._write('DEV:GRPZ:PSU:ACTN:RTOS')

    def doStatus(self, maxage=0):
        t = self._read('DEV:GRPZ:PSU:ACTN')
        if t in ['CLMP', 'HOLD']:
            return status.OK, 'idle'
        else:
            return status.BUSY, 'ramping'

    def _read(self, sig):
        t = self._dev.communicate('READ:%s' % (sig))
        if t.startswith('STAT:%s:' % (sig)):
            return t.replace('STAT:%s:' % (sig), '')
        raise CommunicationError(self, 'Device does not give the right answer'\
                                        ': %s' % (t))

    def _write(self, sig):
        t = self._dev.communicate('SET:%s' % (sig))
        if not t.startswith('STAT:SET:%s:' % (sig)):
            raise CommunicationError(self, 'Device does not accept : %s returns'\
                                    ' %s' % (sig, t))
        t = t.replace('STAT:SET:%s:' % (sig), '')
        if t != 'VALID':
            raise CommunicationError(self, 'Device does not accept : %s' % (sig))

    def doRead(self, maxage=0):
        if self.unit == 'A':
            t = self._read('DEV:GRPZ:PSU:SIG:CURR')
        else:
            t = self._read('DEV:GRPZ:PSU:SIG:FLD')
        return float(t[:-1])

    def doWait(self):
        waitForStatus(self, 0.5)

    def doStop(self):
        t = self._write('DEV:GRPZ:PSU:ACTN:HOLD')

    def doReadRamp(self):
        if self.unit == 'A':
            t = self._read('DEV:GRPZ:PSU:SIG:RCST')
        else:
            t = self._read('DEV:GRPZ:PSU:SIG:RFST')
        return float(t[:-3])

    def doWriteRamp(self, value):
        if value > self.ramplimit:
            raise InvalidValueError(self, 'ramp (%f) is greater the maximum'
                                    ' ramp (%f)' % (value, self.ramplimit))
        if self.unit == 'A':
            self._write('DEV:GRPZ:PSU:SIG:RCST:%f' % float(value))
        else:
            self._write('DEV:GRPZ:PSU:SIG:RFST:%f' % float(value))

#   def doWriteUnit(self, value):
#       if self._cache:
#           self._cache.invalidate(self, 'value')


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
#   Jens Krueger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Class for Oxford magnet consisting of the Mercury iPS power supply
"""

# from PowerSupply import CurrentControl
from IO import StringIO

from nicos.core import Moveable, HasLimits, Param, Override, \
     floatrange, status, oneof, CommunicationError, InvalidValueError, \
     ConfigurationError
from nicos.devices.taco.core import TacoDevice
from nicos.core import SIMULATION


class OxfordMercury(HasLimits, TacoDevice, Moveable):
    """Class for the readout of a Oxford Mercury iPS power supply"""

    taco_class = StringIO
    valuetype = float

    parameter_overrides = {
        'unit':       Override(type=oneof('A', 'T'), default='A', settable=False),
    }

    parameters = {
        'ramp':       Param('Rate of ramping', type=floatrange(0, 2),
                            default=1.8, unit='main/min', settable=True),
        'ramplimit' : Param('Maximum ramp', type=float,
                            unit='main/min', settable=False),
        'scale':      Param('Conversion factor from T to A', type=float,
                            default=31.280, unit='', settable=False),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            if not self._dev.communicate('*IDN?').startswith('IDN'):
                raise CommunicationError(self, 'No Response from Mercury iPS,'
                                               ' please check!')

    def doStart(self, value):
        self.doStop()
        # XXX should switch on Heater switch here, but it is not clear
        # from the handbook how!
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

    def doStop(self):
        self._write('DEV:GRPZ:PSU:ACTN:HOLD')

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



class MercuryAsymmetricalMagnet(HasLimits, Moveable):

    hardware_access = False

    attached_devices = {
        'ps1':   (OxfordMercury, 'First power supply (more current)'),
        'ps2':   (OxfordMercury, 'Second power supply (less current)'),
    }

    # see Magnet handbook table 9.4.1.4
    # mapping asymmetry to (max field, first coil, second coil at max field)
    _scales = {
        70: (2.5, 137.05, 24.19),
        53: (3.0, 147.93, 45.44),
        39: (3.5, 156.73, 68.79),
        25: (4.0, 161.26, 96.76),
        11: (4.5, 160.79, 129.27),
        0:  (5.0, 160.90, 0),
    }

    parameters = {
        'asymmetry': Param('Degree of asymmetry', unit='percent',
                           type=oneof(0, 11, 25, 39, 53, 70), default=70,
                           settable=True),
    }

    parameter_overrides = {
        'unit':    Override(default='T', mandatory=False),
    }

    def doInit(self, mode):
        if self._adevs['ps1'].unit != 'A' or \
            self._adevs['ps2'].unit != 'A':
            raise ConfigurationError(self, 'power supplies should have Ampere '
                                     'unit for asymmetrical mode')

    def doIsAllowed(self, value):
        maxfield, maxcurr1, maxcurr2 = self._scales[self.asymmetry]
        if abs(value) > maxfield:
            return False, 'desired value exceeds maximum field allowed ' \
                'for this asymmetry (%d%%)' % self.asymmetry
        scale = value / maxfield
        ok, why = self._adevs['ps1'].isAllowed(scale * maxcurr1)
        if not ok:
            return ok, why
        return self._adevs['ps2'].isAllowed(scale * maxcurr2)

    def doStart(self, value):
        maxfield, maxcurr1, maxcurr2 = self._scales[self.asymmetry]
        scale = value / maxfield
        self._adevs['ps1'].start(scale * maxcurr1)
        self._adevs['ps2'].start(scale * maxcurr2)

    def doRead(self, maxage=0):
        maxfield, maxcurr1, _maxcurr2 = self._scales[self.asymmetry]
        return self._adevs['ps1'].read(maxage) / maxcurr1 * maxfield

    def doWriteAsymmetry(self, value):
        if abs(self.read(0)) > 0.01:
            raise ConfigurationError(self, 'cannot change asymmetry while the '
                                     'magnet is powered up')

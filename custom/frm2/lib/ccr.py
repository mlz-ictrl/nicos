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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Support classes for the CCR TACO boxes"""

import IO
import time

from nicos.core import Moveable, HasLimits, Override, Param, SIMULATION, \
    ConfigurationError, InvalidValueError, ProgrammingError, oneof, \
    floatrange, tacodev, status, Attach
from nicos.utils import clamp
from nicos.devices.taco.io import NamedDigitalOutput


class CCRControl(HasLimits, Moveable):
    """Combination of the temperature controller for the tube and sample stick
    of the CCR (closed cycle refrigerator) of the SE (sample environment)
    group.

    It gives a single point of controlling the temperature under certain
    conditions:

    * no setpoint change without ramp
    * ramp is limited to 10K/min
    * above 300K, the CCR/coldhead/transfer point stays at 300K,
      while the stick regulates.

    """
    attached_devices = {
        'stick': Attach('Temperaturecontroller for the stick', Moveable),
        'tube':  Attach('Temperaturecontroller for the outer ccr/tube',
                        Moveable),
    }

    parameters = {
        'regulationmode': Param('Preferred regulation point: stick or tube',
                                unit='', type=oneof('stick', 'tube', 'both'),
                                settable=True, chatty=True,
                                category='general'),
        'ramp':           Param('Temperature ramp in K/min', unit='K/min',
                                chatty=True, type=floatrange(0, 100),
                                settable=True, volatile=True, default=1.),
        'setpoint':       Param('Current temperature setpoint', unit='main',
                                category='general'),
    }

    parameter_overrides = {
        'unit':      Override(default='K', type=oneof('K'), settable=False,
                              mandatory=False),
        'abslimits': Override(mandatory=False),
    }

    @property
    def stick(self):
        return self._attached_stick

    @property
    def tube(self):
        return self._attached_tube

    def doInit(self, mode):
        if mode != SIMULATION:
            if self._attached_stick is None or self._attached_tube is None:
                raise ConfigurationError(self, 'Both stick and tube needs to '
                                         'be set for this device!')
            absmin = min(self._attached_tube.absmin, self._attached_stick.absmin)
            absmax = self._attached_stick.absmax
            self._setROParam('abslimits', (absmin, absmax))

    def __start_tube_stick(self, tubetarget, sticktarget):
        ok, why = self._attached_tube.isAllowed(tubetarget)
        if not ok:
            raise InvalidValueError(self, why)
        ok, why = self._attached_stick.isAllowed(sticktarget)
        if not ok:
            raise InvalidValueError(self, why)
        self.log.debug('Moving %s to %r and %s to %r' %
                       (self._attached_tube.name, tubetarget,
                        self._attached_stick, sticktarget))
        try:
            self._attached_tube.start(tubetarget)
        finally:
            self._attached_stick.start(sticktarget)

    def doStart(self, target):
        """Changes the intended setpoint

        Logic is as follows:
        if target is below absmax of the tube, let regulation mode decide if we
        move the stick or the tube or both. The unused one is switched off by
        moving to its absmin value or 0, whatever is bigger.

        If target is above absmax of the tube, we set tube to its absmax and
        the stick to the target. In this case, mode is ignored.

        Normally the absmax of the tube is set to 300K, which is compatible
        with requirements from the SE-group.
        """
        if target < self._attached_tube.absmax:
            if self.regulationmode == 'stick':
                self.__start_tube_stick(max(self._attached_tube.absmin, 0), target)
            elif self.regulationmode == 'tube':
                self.__start_tube_stick(target, max(self._attached_stick.absmin, 0))
            elif self.regulationmode == 'both':
                self.__start_tube_stick(max(self._attached_tube.absmin, target),
                                        max(self._attached_stick.absmin, target))
            else:
                raise ProgrammingError(self, 'unknown mode %r, don\'t know how'
                                       ' to handle it!' % self.regulationmode)
        else:
            self.log.debug('ignoring mode, as target %r is above %s.absmax' %
                           (target, self._attached_tube.name))
            self.__start_tube_stick(self._attached_tube.absmax, target)

    def doRead(self, maxage=0):
        if self._attached_stick.target is not None:
            if self._attached_stick.target >= self._attached_tube.absmax:
                return self._attached_stick.read(maxage)
        if self.regulationmode in ('stick', 'both'):
            return self._attached_stick.read(maxage)
        elif self.regulationmode == 'tube':
            return self._attached_tube.read(maxage)
        else:
            raise ProgrammingError(self, 'unknown mode %r, don\'t know how to '
                                   'handle it!' % self.regulationmode)

    def doPoll(self, n, maxage):
        if n % 50 == 0:
            self._pollParam('setpoint', 60)

    #
    # Parameters
    #

    def __set_param(self, attrname, value):
        self.log.debug('Setting param %s to %r' % (attrname, value))
        setattr(self._attached_tube, attrname, value)
        setattr(self._attached_stick, attrname, value)

    def __get_param(self, attrname):
        # take first match
        tubeval = getattr(self._attached_tube, attrname)
        stickval = getattr(self._attached_stick, attrname)
        if tubeval == stickval:
            res = tubeval
        else:
            self.log.warning('%s.%s (%r) != %s.%s (%r), please set %s.%s to '
                             'the desired value!' %
                             (self._attached_tube.name, attrname, tubeval,
                              self._attached_stick.name, attrname, stickval,
                              self.name, attrname))
            # try to take the 'more important' one
            if self._attached_stick.target is not None and \
               self._attached_stick.target > self._attached_tube.absmax:
                res = stickval
            else:
                if self.regulationmode == 'stick':
                    res = stickval
                elif self.regulationmode == 'tube':
                    res = tubeval
                else:
                    raise ConfigurationError(self, 'Parameters %s.%s and %s.%s'
                                             ' differ! please set them using '
                                             '%s.%s only.' % (
                                                 self._attached_tube.name, attrname,
                                                 self._attached_stick.name, attrname,
                                                 self.name, attrname))

        self.log.debug('param %s is %r' % (attrname, res))
        return res

    def doReadRamp(self):
        # do not return a value the validator would reject, or
        # device creation fails
        ramp = self.__get_param('ramp')
        # this works only for the floatrange type of the ramp parameter!
        rampmin = self.parameters['ramp'].type.fr
        rampmax = self.parameters['ramp'].type.to
        if rampmin <= ramp <= rampmax:
            return ramp
        clampramp = clamp(ramp, rampmin, rampmax)
        self.log.warning('Ramp parameter %.3g is outside of the allowed range '
                         '%.3g..%.3g, setting it to %.3g' % (
                             ramp, rampmin, rampmax, clampramp))
        # clamp read value to allowed range and re-set it
        return self.doWriteRamp(clampramp)

    def doWriteRamp(self, value):
        # this works only for the floatrange type of the ramp parameter!
        rampmin = self.parameters['ramp'].type.fr
        rampmax = self.parameters['ramp'].type.to
        if value == 0.0:
            value = rampmax
            self.log.warning('Ramp rate of 0 is deprecated, using %d '
                             'K/min instead' % value)
        self.__set_param('ramp', clamp(value, rampmin, rampmax))
        return self.__get_param('ramp')

    def doWriteRegulationmode(self, value):
        self.log.info('To use the new regulationmode %r, please start/move '
                      '%s...' % (value, self.name))

    def doReadSetpoint(self):
        if self._attached_stick.target is not None:
            if self._attached_stick.target >= self._attached_tube.absmax:
                return self._attached_stick.setpoint
        # take the more important one, closer to the sample.
        if self.regulationmode in ('stick', 'both'):
            return self._attached_stick.setpoint
        elif self.regulationmode == 'tube':
            return self._attached_tube.setpoint
        else:
            raise ProgrammingError(self, 'unknown mode %r, don\'t know how to '
                                   'handle it!' % self.regulationmode)


class CompressorSwitch(NamedDigitalOutput):
    """ The CCR box has two separate switches to switch the compressor 'on' and
    'off'.

    The access is realized via two TACO devices, the current state is
    given by a third device.

    The 'on' device is the inherited TACO device.
    """
    parameters = {
        'offdev':  Param('Device to switch the compressor off',
                         type=tacodev, mandatory=True, preinit=True),
        'readback': Param('Device to read back the compressor state indicator',
                          type=tacodev, mandatory=True, preinit=True),
        'statusdev': Param('Device to read out the compressor state',
                           type=tacodev, mandatory=True, preinit=True),
        'sleeptime': Param('Time to wait after switching',
                           type=float, default=0.1),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        if mode != SIMULATION:
            self._off = self._create_client(
                self.offdev, IO.DigitalOutput, resetok=True, timeout=None)
            self._readback = self._create_client(
                self.readback, IO.DigitalInput, resetok=True, timeout=None)
            self._status = self._create_client(
                self.statusdev, IO.DigitalInput, resetok=True, timeout=None)

    def doStart(self, target):
        value = self.mapping.get(target, target)
        if value == self._read():
            return
        if value == 1:
            self._taco_guard(self._dev.write, 1)
        else:
            self._taco_guard(self._off.write, 1)
        time.sleep(self.sleeptime)

    def _read(self):
        return self._taco_guard(self._readback.read)

    def doRead(self, maxage=0):
        value = self._read()
        return self._reverse.get(value, value)

    def doStatus(self, maxage=0):
        target = self.mapping.get(self.target, self.target)
        if target == self._read():
            if target == 1:
                return status.OK, 'idle, on'
        val = ~self._taco_guard(self._status.read) & 0x1FF
        if (val == 0x1FF):
            return status.ERROR, 'Offline (not connected)'
        elif (val & 1) == 1:
            return status.ERROR, 'Oil missing'
        elif (val & 4) == 4:
            return status.ERROR, 'Motor temperature too high'
        elif val == 8:
            return status.OK, 'idle, bypass open'
        elif (val & 0x10) == 0x10:
            return status.ERROR, 'Power failure'
        elif (val & 0x80) == 0x80:
            return status.ERROR, 'Gas temperature too high'
        elif (val & 0x100) == 0x100:
            return status.ERROR, 'Gas return pressure too high'
        elif (val & 2) == 2:
            if (val & 0x20) == 0x20:
                return status.ERROR, 'Water inlet temperature is too high'
            elif (val & 0x40) == 0x40:
                return status.ERROR, 'Water outlet temperature is too low' \
                    ' (flow is too low)'
            return status.OK, 'idle, off'
        else:
            return status.UNKNOWN, 'UNKNOWN'
        return status.ERROR, 'target not reached'

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

"""Definition special power supply class for CHARM detector."""

from nicos import session
from nicos.core import status
from nicos.core.constants import POLLER
from nicos.core.device import Moveable, Readable
from nicos.core.errors import ConfigurationError, ModeError, NicosError, \
    PositionError
from nicos.core.params import Attach, Override, Param, dictof, oneof
from nicos.devices.abstract import MappedMoveable
from nicos.devices.generic.sequence import SeqDev, SeqParam, SequencerMixin
from nicos.utils import num_sort


class SeqRampParam(SeqParam):
    """Special parameter sequence.

    Since the parameter will be written on the hardware, and the hardware does
    not return the set parameter value exactly (due to rounding effects)
    a precision is needed to verify the current value.

    The number of retries is needed due to the time needed to apply the value
    on the hardware
    """

    precision = 0.01
    nretries = 2

    def __init__(self, dev, value):
        SeqParam.__init__(self, dev=dev, paramname='ramp', value=value)

    def run(self):
        setattr(self.dev, self.paramname, self.value)
        for _ in range(self.nretries):
            if self.isCompleted():
                return
            session.delay(0.2)
            self.log.info('waiting')
        raise NicosError('Setting Parameter %s of dev %s to %r failed!' % (
            self.paramname, self.dev, self.value))

    def isCompleted(self):
        return abs(
            getattr(self.dev, self.paramname) - self.value) <= self.precision


class HVSwitch(SequencerMixin, MappedMoveable):
    """High voltage convenience switching device for the CHARM detector."""

    valuetype = oneof('on', 'off', 'safe')

    attached_devices = {
        'anodes': Attach('HV channels for the anodes',
                         Moveable, multiple=[2, 9]),
        'banodes': Attach('HV channels for the boundary anodes',
                          Moveable, multiple=[1, 8]),
        'cathodes': Attach('HV channels for the boundary cathodes',
                           Moveable, multiple=2),
        'window': Attach('HV channel for the window',
                         Moveable, multiple=1),
        'trip': Attach('Devices signaling a trip on the hardware',
                       Readable),
    }

    parameters = {
        '_tripped': Param('Indicator for hardware trip',
                          type=bool, internal=True, default=False),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'fallback': Override(default='unknown'),
        'mapping': Override(type=dictof(str, dictof(str, float))),
    }

    def doInit(self, mode):
        if self.fallback in self.mapping:
            raise ConfigurationError(self, 'Value of fallback parameter is '
                                     'not allowed to be in the mapping!')
        self._devices = {
            dev.name: dev for dev in (
                self._attached_anodes + self._attached_banodes +
                self._attached_cathodes + self._attached_window)
        }

        if len(self._attached_anodes) != len(self._attached_banodes) + 1:
            raise ConfigurationError(self, 'Number of anode devices must be '
                                     'the number of boundary anodes + 1: %d, '
                                     '%d' % (
                                         len(self.anodes), len(self.banodes)))
        # if not self.relax_mapping:
        #     self.valuetype = oneof(*sorted(self.mapping, key=num_sort))

        for value in sorted(self.mapping, key=num_sort):
            try:
                self.valuetype(value)
            except ValueError as err:
                raise ConfigurationError(
                    self, '%r not allowed as key in mapping. %s' % (
                        value, err)) from err

    def doIsAllowed(self, target):
        if target == 'off':
            ok = True
        else:
            ok = not self._tripped and not self._attached_trip.read(0)
        return ok, '' if ok else 'hardware is tripped'

    def doStop(self):
        if not self._tripped:
            SequencerMixin.doStop(self)
        else:
            raise ModeError(self, "can't be stopped, device is tripped.")

    def doReset(self):
        if self._tripped:
            if self.doStatus(0)[0] == status.BUSY or self._hardware_tripped():
                raise ModeError(self, "can't reset device. Hardware is tripped")
        SequencerMixin.doReset(self)
        self._setROParam('_tripped', False)

    def doPoll(self, n, maxage):
        if not self._tripped and session.sessiontype == POLLER and \
           self._hardware_tripped():
            self._setROParam('_tripped', True)

    def _hardware_tripped(self):
        return self._attached_trip.read(0) == 'Trip'

    def _generateSequence(self, target):
        anodes = self._attached_anodes + self._attached_banodes
        seq = [
            [SeqDev(dev, self.mapping[target][dev.name])
             for dev in self._attached_window],
            [SeqDev(dev, self.mapping[target][dev.name]) for dev in anodes],
            [SeqDev(dev, self.mapping[target][dev.name])
             for dev in self._attached_cathodes],
        ]
        return seq

    def _is_at_target(self, pos, target):
        # if values are exact the same
        if pos == target:
            return True
        for dev in pos:
            if not self._devices[dev].isAtTarget(pos[dev], target[dev]):
                return False
        return True

    def _mapReadValue(self, value):
        for val in self.mapping:
            if self._is_at_target(value, self.mapping[val]):
                return val
        if self.fallback is not None:
            return self.fallback
        else:
            raise PositionError(self, 'unknown unmapped position %r' % value)

    def _readRaw(self, maxage=0):
        return {dev.name: dev.read(maxage) for dev in self._devices.values()}

    def _startRaw(self, target):
        ramp = self.mapping[self.target]['ramp']
        seq = self._generateSequence(self.target)
        if self.target in ['off', 'safe']:
            seq.reverse()
        self._startSequence(
            [SeqRampParam(dev, ramp)
             for dev in self._attached_anodes + self._attached_banodes +
             self._attached_cathodes] +
            [SeqRampParam(dev, -ramp) for dev in self._attached_window] + seq)

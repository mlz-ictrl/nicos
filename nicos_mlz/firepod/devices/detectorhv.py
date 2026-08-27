# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""Classes to handle the HV of the FirePOD detector."""

from nicos.core.constants import SIMULATION
from nicos.core.device import Moveable
from nicos.core.errors import MoveError, PositionError
from nicos.core.params import Attach, Override, Param, dictof, floatrange, \
    oneof, tupleof
from nicos.devices.abstract import MappedMoveable, Motor
from nicos.devices.generic.sequence import SeqDev, SeqParam, SequencerMixin


class DetectorHVChannelSwitch(SequencerMixin, MappedMoveable):
    """Single HV switch for one detector module."""

    attached_devices = {
        'drift': Attach("HV of the 'drift'", Motor),
        'anode': Attach('HV of the anode', Motor),
    }

    parameters = {
        'ramp': Param('Change speed of the HV in V/min',
                      type=floatrange(1 * 60, 255 * 60), settable=True,
                      default=5*60),
    }

    parameter_overrides = {
        'mapping':  Override(type=dictof(oneof('off', 'on'),
                                         tupleof(float, float)),
                             default={'off': (0, 0), 'on': (-1000, 2650)},
                             mandatory=False),
        'fallback': Override(default='intermediate', prefercache=False,
                             settable=False),
    }

    @property
    def _devices(self):
        return (self._attached_drift, self._attached_anode)

    def _generateSequence(self, target):
        seq = [
            SeqParam(dev=dev, paramname='speed', value=self.ramp / 60)
            for dev in self._devices
        ]
        if self.target == 'on':
            seq.extend([
                SeqDev(dev, t, stoppable=True)
                for dev, t in zip(self._devices, target)
            ])
        else:
            seq.extend([
                SeqDev(dev, t, stoppable=True)
                for dev, t in zip(reversed(self._devices), reversed(target))
            ])
        return seq

    def _is_at_target(self, values, targets):
        for dev, val, target in zip(self._devices, values, targets):
            if not dev.isAtTarget(val, target):
                return False
        return True

    def _mapReadValue(self, value):
        for val, target in self.mapping.items():
            if self._is_at_target(value, target):
                return val
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, f'unknown unmapped position {value!r}')

    def _readRaw(self, maxage=0):
        return [dev.read(maxage) for dev in self._devices]

    def _startRaw(self, target):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                f'running (at {self._seq_status[1]})!')
        self._startSequence(self._generateSequence(target))

    def doReset(self):
        SequencerMixin.doReset(self)
        for d in self._devices:
            d.reset()


class DetectorHV(Moveable):
    """HV switch for a list of detector modules.

    The detector module have to be of type `DetectorHVChannelSwitch`.
    """

    attached_devices = {
        'channels': Attach('Devices to switch the HV of each detector',
                           DetectorHVChannelSwitch, multiple=True),
    }

    parameter_overrides = {
        'unit':  Override(default='', mandatory=False, settable=False),
    }

    valuetype = oneof('off', 'on')

    def doStart(self, target):
        for dev in self._attached_channels:
            dev.move(target)

    def doRead(self, maxage=0):
        pos = [dev.read(maxage) for dev in self._attached_channels]
        if all(val == pos[0] for val in pos):
            return pos[0]
        return self._attached_channels[0].fallback

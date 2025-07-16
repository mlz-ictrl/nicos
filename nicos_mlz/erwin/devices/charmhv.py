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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Definition special power supply class for CHARM detector."""

from time import time as currenttime

from nicos import session
from nicos.core import Attach, Override, Param, dictof, floatrange, listof, \
    oneof, status, tupleof
from nicos.core.constants import POLLER, SIMULATION
from nicos.core.device import Moveable, Readable
from nicos.core.errors import ConfigurationError, ModeError, MoveError, \
    NicosError, PositionError
from nicos.devices.abstract import MappedMoveable
from nicos.devices.generic.sequence import SeqDev, SeqParam, SeqSleep, \
    SequencerMixin


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
            session.log.info('waiting')
        raise NicosError('Setting Parameter %s of dev %s to %r failed!' % (
            self.paramname, self.dev, self.value))

    def isCompleted(self):
        return abs(
            getattr(self.dev, self.paramname) - self.value) <= self.precision


class HVSwitch(SequencerMixin, MappedMoveable):
    """High voltage convenience switching device for the CHARM detector."""

    hardware_access = False

    attached_devices = {
        'anodes': Attach('HV channels for the anodes',
                         Moveable, multiple=[2, 9]),
        'banodes': Attach('HV channels for the boundary anodes',
                          Moveable, multiple=[1, 8]),
        'edges': Attach('HV channels for the boundary cathodes',
                        Moveable, multiple=2),
        'window': Attach('HV channel for the window',
                         Moveable, multiple=1),
    }

    parameters = {
        'tripped': Param('Indicator for hardware trip',
                         type=bool, internal=True, default=False),
        'lasthv': Param('When was hv applied last (timestamp)',
                        type=float, internal=True, default=0.0,
                        mandatory=False, settable=False),
        'onstate': Param('Value indicating the HV is switched on',
                         type=str, default='on'),
        'offstate': Param('Value indicating the HV is switched on',
                          type=str, default='off'),
        'safestate': Param('Value indicating the HV is switched to safe state',
                           type=str, default='safe'),
        'maxofftime': Param('Maximum allowed Off-time for fast ramp-up',
                            type=int, unit='s', default=12 * 3600),
        'slowramp': Param('Slow ramp-up speed (volt per minute)',
                          type=floatrange(0), unit='main/min', default=90),
        'fastramp': Param('Fast ramp-up speed (volt per minute)',
                          type=float, unit='main/min', default=360),
        'rampsteps': Param('Cold-ramp-up sequence (voltage, stabilize_minutes)',
                           type=listof(tupleof(floatrange(0), floatrange(0))),
                           unit='',
                           default=[
                               (500, 3),
                               (1000, 3),
                               (1500, 3),
                               (1750, 3),
                               (1950, 3),
                               ]),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'fallback': Override(default='unknown'),
        'mapping': Override(type=dictof(str, dictof(str, float))),
    }

    @property
    def _anodes(self):
        return self._attached_anodes + self._attached_banodes

    @property
    def _devices(self):
        return {
            dev.name: dev for dev in (
                self._anodes + self._attached_edges + self._attached_window)
        }

    def doInit(self, mode):
        self.valuetype = oneof(*self.mapping)

        if self.fallback in self.mapping:
            raise ConfigurationError(self, 'Value of fallback parameter is '
                                     'not allowed to be in the mapping!')

        if len(self._attached_anodes) != len(self._attached_banodes) + 1:
            raise ConfigurationError(self, 'Number of boundary anode devices '
                                     'must be the number of anodes - 1: '
                                     f'{len(self.banodes)}, {len(self.anodes)}')

        for value in [self.onstate, self.offstate, self.safestate]:
            if value not in self.mapping:
                raise ConfigurationError(
                    self, f'Parameter "{value}state" not in {list(self.mapping)}')

        if session.sessiontype != POLLER:
            for d in self._devices.values():
                d.enable()

    def doStatus(self, maxage=0):
        stat, statmsg = SequencerMixin.doStatus(self, maxage)
        if stat == status.ERROR:
            if not self.tripped and 'tripped' in statmsg:
                self._setROParam('tripped', True)
        elif stat == status.WARN and self.target != self.onstate:
            return status.OK, 'idle'
        return stat, statmsg

    def doIsAllowed(self, target):
        if target == self.offstate:
            return True, ''
        ok = not self.tripped
        return ok, '' if ok else 'hardware is tripped'

    def doStop(self):
        if self.tripped:
            raise ModeError(self, "can't be stopped, device is tripped.")
        SequencerMixin.doStop(self)

    def doReset(self):
        if self.tripped:
            if self.doStatus(0)[0] == status.BUSY or self.tripped:
                raise ModeError(self, "can't reset device. Hardware is tripped")
        SequencerMixin.doReset(self)
        self._setROParam('tripped', False)

    def _is_at_target(self, pos, target):
        # if values are exact the same
        if pos == {k: target[k] for k in pos}:
            return True
        for dev in pos:
            # If there are some warnlimits defined, the difference will be used
            # as precision value
            device = self._devices[dev]
            if wlims := device.warnlimits:
                prec = target[dev] - wlims[0], wlims[1] - target[dev]
                if not (target[dev] - prec[0] <= pos[dev] <= target[dev] + prec[1]):
                    self.log.warning('%s: %s %s %s', dev, pos[dev], target[dev], prec)
                    return False
            elif not self._devices[dev].isAtTarget(pos[dev], target[dev]):
                return False
        return True

    def _mapReadValue(self, value):
        for val in self.mapping:
            if self._is_at_target(value, self.mapping[val]):
                return val
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown unmapped position %r' % value)

    def _readRaw(self, maxage=0):
        return {dev.name: dev.read(maxage) for dev in self._devices.values()}

    def _cold_start(self, target):
        if target != self.onstate:
            return False
        # check off time
        return not self.lasthv or currenttime() - self.lasthv > self.maxofftime

    def _move_downwards(self, target):
        """Check if the target is below the current value."""
        if target == self.offstate:
            return True
        if target == self.onstate:
            return False
        pos = self.read(0)
        if pos == self.onstate:  # ON -> SAFE
            return True
        return False

    def _generateSequence(self, target):
        ramp = self.slowramp
        if not self._cold_start(target):
            ramp = self.fastramp
        seq = [
            tuple(SeqDev(dev, self.mapping[target][dev.name])
                  for dev in self._attached_window),
            tuple(SeqDev(dev, self.mapping[target][dev.name])
                  for dev in self._attached_edges),
        ]
        if self._cold_start(target):
            for steptarget, waittime in self.rampsteps:
                seq.append(tuple(SeqDev(dev, steptarget)
                                 for dev in self._anodes))
                seq.append(SeqSleep(waittime * 60))
        seq.append(tuple(SeqDev(dev, self.mapping[target][dev.name])
                         for dev in self._anodes))
        if self._move_downwards('target'):
            seq.reverse()
        return [SeqRampParam(d, ramp) for d in self._devices.values()] + seq

    def _startRaw(self, target):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(self.target))

    def doRead(self, maxage=0):
        val = MappedMoveable.doRead(self, maxage)
        if val == self.onstate:
            self._setROParam('lasthv', currenttime())
        return val


class HVOffDuration(Readable):

    attached_devices = {
        'hv_supply': Attach('HV Device', HVSwitch),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True),
    }

    valuetype = str

    def doRead(self, maxage=0):
        if self._attached_hv_supply:
            secs = currenttime() - self._attached_hv_supply.lasthv
            hours = int(secs / 3600)
            mins = int(secs / 60) % 60
            secs = int(secs) % 60
            return '%g:%02d:%02d' % (hours, mins, secs)
        return 'never'

    def doReadUnit(self):
        return ''

    def doStatus(self, maxage=0):
        stat, statmsg = self._attached_hv_supply.status(maxage)
        if stat == status.WARN:
            return status.OK, ''
        return stat, statmsg


class HVTrip(Readable):

    attached_devices = {
        'hv_supply': Attach('HV Device', HVSwitch),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True),
    }

    valuetype = str

    def doRead(self, maxage=0):
        return 'Tripped' if self._attached_hv_supply.tripped else ''

    def doReadUnit(self):
        return ''

    def doStatus(self, maxage=0):
        stat, statmsg = self._attached_hv_supply.status(maxage)
        if stat == status.WARN:
            return status.OK, ''
        return stat, statmsg

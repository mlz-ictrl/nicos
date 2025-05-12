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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special device for Sans1 High Voltage supply"""


from time import localtime, strftime, time as currenttime

from nicos.core import Attach, HasLimits, HasPrecision, InvalidValueError, \
    Moveable, Override, Param, PositionError, Readable, listof, status, \
    tupleof
from nicos.devices.generic.sequence import BaseSequencer, \
    LockedDevice as NicosLockedDevice, SeqDev, SeqMethod, SeqParam, SeqSleep
from nicos.devices.generic.switcher import Switcher


class VoltageSwitcher(Switcher):
    """mapping is now state:(value, precision)"""
    def _mapTargetValue(self, target):
        if target not in self.mapping:
            positions = ', '.join(repr(pos) for pos in self.mapping)
            raise InvalidValueError(self, '%r is an invalid position for '
                                    'this device; valid positions are %s'
                                    % (target, positions))
        return self.mapping.get(target)[0]

    def _mapReadValue(self, value):
        """Override default inverse mapping to allow a deviation <= precision"""
        for name, values in self.mapping.items():
            pos, prec = values
            if pos == value:
                return name
            elif prec:
                if abs(pos - value) <= prec:
                    return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s: %s' %
                            (self._attached_moveable,
                             self._attached_moveable.format(value, True))
                            )

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = self._attached_moveable.status(maxage)
        if move_status[0] == status.BUSY:
            if self.target == 'LOW' and self._attached_moveable.read(0) < 70:
                return status.OK, 'below 70V'
        return move_status


class HV(HasLimits, BaseSequencer):
    valuetype = float
    attached_devices = {
        'supply':     Attach('NICOS Device for the high voltage supply',
                             Moveable),
        'discharger': Attach('Switch to activate the discharge resistors',
                             Moveable),
        'interlock':  Attach('Assume IDLE if set and Target is set to 0',
                             Readable),
    }

    parameters = {
        'ramp':       Param('Current ramp speed (volt per minute)',
                            type=int, unit='main/min', settable=True,
                            volatile=True),
        'lasthv':     Param('When was hv applied last (timestamp)',
                            type=float, internal=True, default=0.0,
                            mandatory=False, settable=False),
        'maxofftime': Param('Maximum allowed Off-time for fast ramp-up',
                            type=int, unit='s', default=4 * 3600),
        'slowramp':   Param('Slow ramp-up speed (volt per minute)',
                            type=int, unit='main/min', default=120),
        'fastramp':   Param('Fast ramp-up speed (volt per minute)',
                            type=int, unit='main/min', default=1200),
        'rampsteps':  Param('Cold-ramp-up sequence (voltage, stabilize_minutes)',
                            type=listof(tupleof(int, int)), unit='',
                            default=[(70, 3),
                                     (300, 3),
                                     (500, 3),
                                     (800, 3),
                                     (1100, 3),
                                     (1400, 3),
                                     (1500, 10)]),
    }

    parameter_overrides = {
        'abslimits':  Override(default=(0, 1500), mandatory=False),
        'unit':       Override(default='V', mandatory=False, settable=False),
    }

    def _generateSequence(self, target):
        hvdev = self._attached_supply
        disdev = self._attached_discharger
        seq = [SeqMethod(hvdev, 'stop'), SeqMethod(hvdev, 'wait')]

        now = currenttime()

        # below first rampstep is treated as poweroff
        if target <= self.rampsteps[0][0]:
            # fast ramp
            seq.append(SeqParam(hvdev, 'ramp', self.fastramp))
            seq.append(SeqDev(disdev, 1 if self.read() > target else 0))
            if self.read() > self.rampsteps[0][0]:
                seq.append(SeqDev(hvdev, self.rampsteps[0][0]))
            seq.append(SeqMethod(hvdev, 'start', target))
            return seq

        # check off time
        if self.lasthv and now - self.lasthv <= self.maxofftime:
            # short ramp up sequence
            seq.append(SeqParam(hvdev, 'ramp', self.fastramp))
            seq.append(SeqDev(disdev, 1 if self.read() > target else 0))
            seq.append(SeqDev(hvdev, target))
            # retry if target not reached
            seq.append(SeqMethod(hvdev, 'start', target))
            return seq

        # long sequence
        self.log.warning('Voltage was down for more than %.2g hours, '
                         'ramping up slowly, be patient!',
                         self.maxofftime / 3600)

        self.log.info('Voltage will be ready around %s', strftime(
            '%X', localtime(now + self.doTime(self.doRead(0), target))))

        seq.append(SeqParam(hvdev, 'ramp', self.slowramp))
        seq.append(SeqDev(disdev, 0))
        for voltage, minutes in self.rampsteps:
            # check for last point in sequence
            if target <= voltage:
                seq.append(SeqDev(hvdev, target))
                seq.append(SeqSleep(minutes * 60, 'Stabilizing HV for %d minutes'
                                    % minutes))
                break
            else:  # append
                seq.append(SeqDev(hvdev, voltage))
                seq.append(SeqSleep(minutes * 60, 'Stabilizing HV for %d minutes'
                                    % minutes))
        seq.append(SeqDev(hvdev, target))  # be sure...
        seq.append(SeqMethod(hvdev, 'poll'))  # force a read
        return seq

    def _waitFailed(self, step, action, exc_info):
        # signal single retry of the action
        return True

    def _runFailed(self, step, action, exc_info):
        # signal single retry of the action
        return 1

    def doRead(self, maxage=0):
        voltage = self._attached_supply.read(maxage)
        # everything below the last rampstep is no HV yet...
        # bugfix: avoid floating point rounding errors
        if voltage >= (self.rampsteps[-1][0] - 0.001):
            # just assigning does not work inside poller, but we want that!
            self._setROParam('lasthv', currenttime())
        return voltage

    def doIsAllowed(self, target):
        return self._attached_supply.isAllowed(target)

    def doTime(self, old_value, target):
        # duration is in minutes...
        duration = abs(old_value - target) / float(self.fastramp)
        if not self.lasthv or (currenttime() - self.lasthv > self.maxofftime):
            # cold start
            fromVolts = 0
            for volts, waiting in self.rampsteps:
                duration += waiting
                duration += (min(volts, target) - fromVolts) / float(self.slowramp)
                fromVolts = volts
                if volts >= target:
                    break
        return duration * 60.

    # convenience stuff
    def doReadRamp(self):
        return self._attached_supply.ramp

    def doWriteRamp(self, value):
        self._attached_supply.ramp = value
        return self.doReadRamp()


class HVOffDuration(Readable):
    attached_devices = {
        'hv_supply': Attach('HV Device', HV),
    }
    parameter_overrides = {
        'unit': Override(mandatory=False),
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


class LockedDevice(HasPrecision, NicosLockedDevice):

    def doStart(self, target):
        if abs(self.read(0) - target) >= self.precision:
            NicosLockedDevice.doStart(self, target)

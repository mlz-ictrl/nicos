#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Param, Override, none_or, Moveable, listof, tupleof
from nicos.devices.generic.sequence import BaseSequencer, LockedDevice, \
     SeqDev, SeqMethod, SeqParam, SeqSleep

class HVLock(LockedDevice):
    """A LockedDevice which cowardly refuse to go where it is already"""
    def doStart(self, target):
        if target != self.read():
            BaseSequencer.doStart(self, target)

class Sans1HV(BaseSequencer):
    attached_devices = {
        'supply'     : (Moveable, 'NICOS Device for the highvoltage supply'),
        'discharger' : (Moveable, 'Switch to activate the discharge resistors'),
    }

    parameters = {
        'ramp'   : Param('current ramp speed (volt per minute)',
                          type=int, unit='main/min', settable=True, volatile=True),
        'lasthv'   : Param('when was hv applied last (timestamp)',
                              type=none_or(float), userparam=False,
                              mandatory=False, settable=False),
        'maxofftime'   : Param('Maximum allowed Off-time for fast ramp-up',
                              type=int, unit='s', default=4 * 3600),
        'slowramp'   : Param('slow ramp-up speed (volt per minute)',
                              type=int, unit='main/min', default=120),
        'fastramp'   : Param('Fast ramp-up speed (volt per minute)',
                              type=int, unit='main/min', default=1200),
        'rampsteps'   : Param('Cold-ramp-up sequence (voltage, stabilize_minutes)',
                              type=listof(tupleof(int,int)), unit='',
                              default=[(100, 5),
                                       (300, 3),
                                       (500, 3),
                                       (800, 3),
                                       (1100, 3),
                                       (1350, 3),
                                       (1450, 3),
                                       (1530, 10)]),
    }

    parameter_overrides = {
        'abslimits' : Override(default=(0, 1530), mandatory=False),
        'unit'      : Override(default='V', mandatory=False, settable=False),
    }


    def _generateSequence(self, target, *args, **kwargs):
        hvdev = self._adevs['supply']
        disdev = self._adevs['discharger']
        seq = []

        now = currenttime()

        # below first rampstep is treated as poweroff
        if target < self.rampsteps[0][0]:
            # fast ramp
            seq.append(SeqParam(hvdev, 'ramp', self.fastramp))
            seq.append(SeqDev(disdev, 1 if self.read() > target else 0))
            seq.append(SeqDev(hvdev, target))
            self._setROParam('lasthv', now)
            return seq

        # check off time
        if self.lasthv and now - self.lasthv <= self.maxofftime:
            # short ramp up sequence
            seq.append(SeqParam(hvdev, 'ramp', self.fastramp))
            seq.append(SeqDev(disdev, 1 if self.read() > target else 0))
            seq.append(SeqDev(hvdev, target))
            return seq

        # long sequence
        self.log.warning('Voltage was down for more than %.2g hours, '
                         'ramping up slowly, be patient!' %
                         (self.maxofftime / 3600))

        self.log.info('Voltage will be ready around %s' %
                       strftime('%X', localtime(now +
                                self.doTime(self.doRead(0), target))))

        seq.append(SeqParam(hvdev, 'ramp', self.slowramp))
        seq.append(SeqDev(disdev, 0))
        for voltage, minutes in self.rampsteps:
            # check for last point in sequence
            if target <= voltage:
                seq.append(SeqDev(hvdev, target))
                seq.append(SeqSleep(minutes * 60, 'Stabilizing HV for %d minutes'
                            % minutes))
                break
            else: # append
                seq.append(SeqDev(hvdev, voltage))
                seq.append(SeqSleep(minutes * 60, 'Stabilizing HV for %d minutes'
                            % minutes))
        seq.append(SeqDev(hvdev, target)) # be sure...
        seq.append(SeqMethod(hvdev, 'poll')) # force a read
        return seq

    def doRead(self, maxage=0):
        voltage = self._adevs['supply'].read(maxage)
        # everything below the first rampstep is no HV yet...
        if voltage >= self.rampsteps[0][0]:
            # just assigning does not work inside poller, but we want that!
            self._setROParam('lasthv', currenttime())
        return voltage

    def doIsAllowed(self, target):
        return self._adevs['supply'].isAllowed(target)

    def doTime(self, pos, target):
        # duration is in minutes...
        duration = abs(pos - target) / float(self.fastramp)
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
        return self._adevs['supply'].ramp

    def doWriteRamp(self, value):
        self._adevs['supply'].ramp = value
        return self.doReadRamp()

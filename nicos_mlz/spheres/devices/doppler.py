#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# ****************************************************************************

"""Doppler device for SPHERES"""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands.basic import sleep
from nicos.core import SIMULATION, UsageError, dictwith, floatrange, \
    oneofdict_or, status
from nicos.core.params import Attach, Param
from nicos.devices.generic.sequence import SeqCall, SeqDev, SequencerMixin
from nicos.devices.generic.switcher import MultiSwitcher
from nicos.devices.tango import NamedDigitalOutput, VectorInput
from nicos.protocols.daemon import STATUS_INBREAK
from nicos.pycompat import number_types

ELASTIC =   'elastic'
INELASTIC = 'inelastic'
SPEED =     'speed'
AMPLITUDE = 'amplitude'


class AcqDoppler(VectorInput):
    """Doppler values as read by the Detector"""

    def doRead(self, maxage=0):
        speed, ampl = self._dev.getDopplerValues()
        ampl *= 1000

        return speed, ampl

    def changeDummySpeed(self, target):
        self._dev.dummy_doppvel = target


class Doppler(SequencerMixin, MultiSwitcher):
    """Device to change the dopplerspeed.
    It also compares the speed and amplitude 'seen' by the SIS detector to
    the values set in the doppler and notifies the user if these values do
    not match."""

    parameters = {
        'margins': Param('margin for readout errors in refdevices',
                         dictwith(speed=float, amplitude=float),
                         default=dict(speed=.0, amplitude=.0), settable=True),
        'maxacqdelay': Param('maximum time to wait for the detector to adjust '
                             'when a measurement is started in seconds',
                             int, default=50, settable=True),
        'customrange': Param('min and max for custom values',
                             tuple, settable=False, volatile=True)
    }

    attached_devices = {
        'switch': Attach('The on/off switch of the doppler',
                         NamedDigitalOutput),
        'acq':    Attach('The doppler as seen by the SIS-Detector',
                         AcqDoppler),
    }

    def doInit(self, mode):
        MultiSwitcher.doInit(self, mode)

        self._sm_values = sorted([x for x in self.mapping
                                  if isinstance(x, number_types)])[1:]

        named_vals = {k: v[0] for k, v in self.mapping.items()}

        self.valuetype = oneofdict_or(named_vals,
                                      floatrange(0,
                                                 self._sm_values[-1]))

    def doRead(self, maxage=0):
        if self._attached_switch.read() == 'off':
            return 0
        return self._mapReadValue(self._readRaw(maxage))

    def doStart(self, target):
        # value is out of range
        if target not in self.mapping and not self.inRange(target):
            raise UsageError('Values have to be within %.2f and %.2f.' %
                             (self.customrange[0], self.customrange[-1]))

        # if acq runs in dummy mode this will change the speed accordingly
        # otherwise this will be ignored in entangle
        self._attached_acq.changeDummySpeed(target)

        # a custom value has been requested
        if target not in self.mapping:
            self.log.warning('Moving doppler to a speed which is not in the '
                             'configured setup (but within range).')

        for entry in self._sm_values:
            if target <= entry:
                self._startRaw((target, self.mapping[entry][1]))
                return

    def _startRaw(self, target):
        if self._mode != SIMULATION \
                and session.daemon_device._controller.status == STATUS_INBREAK:
            raise UsageError('Doppler speed can not be changed when script is '
                             'paused.')
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
            else:
                self._seq_thread.join(0)
            self._seq_thread = None

        if not self.waitForAcq(10):
            return

        seq = list()
        # to change the doppler speed it has to be stopped first
        seq.append(SeqDev(self._attached_switch, 'off'))
        seq.append(SeqCall(session.delay, 0.5))
        if target[0] != 0:
            seq.append(SeqCall(MultiSwitcher._startRaw, self, target))
            seq.append(SeqDev(self._attached_switch, 'on'))

        seq.append(SeqCall(self.waitForSync, target))
        self._startSequence(seq)

    def acqIsCounting(self):
        return self._attached_acq.status() == (status.BUSY, 'counting')

    def waitForAcq(self, retries):
        if not self.acqIsCounting():
            return True

        while retries:
            sleep(0.5)
            retries -= 1
            if not self.acqIsCounting():
                return True
        self.log.warning('Doppler speed can not be changed while '
                         'SIS is counting.')
        return False

    def waitForSync(self, target):
        if session.mode == SIMULATION:
            return

        elif target[0] == 0:
            while True:
                if self.withinMargins(self._attached_acq.read()[0], 0, SPEED):
                    return
                session.delay(1)
        else:
            while True:
                acq_speed, acq_ampl = self._attached_acq.read()
                speed, ampl = self._readRaw()
                # acq and doppler are back in sync after changing the doppler
                if self.withinMargins(acq_speed, speed, SPEED) \
                        and self.withinMargins(acq_ampl, ampl, AMPLITUDE):
                    return
                session.delay(1)

    def withinMargins(self, value, target, name):
        return target - self.margins[name] < value < target + self.margins[name]

    def doStatus(self, maxage=0):
        # when the sequence is running only it's status is of interest
        if self._seq_status[0] != status.OK:
            return self._seq_status

        # otherwise the actual doppler status is relevant
        acq_speed, acq_ampl = self._attached_acq.read()
        speed, ampl = self._readRaw()

        if self._attached_switch.read() == 'off':
            if not self.withinMargins(acq_speed, 0, SPEED):
                return (status.WARN, 'detector registers movement of the '
                                     'doppler, although it has been stopped.')
        elif not self.withinMargins(acq_speed, speed, SPEED):
            return (status.WARN, 'detector observes a speed differing '
                                 'from the dopplerspeed')
        elif not self.withinMargins(acq_ampl, ampl, AMPLITUDE):
            return (status.WARN, 'detector observes an amplitude differing '
                                 'from the doppleramplitude')
        elif round(speed, 2) not in self._sm_values \
                and self.inRange(speed):
            return status.OK, 'Doppler runs at custom speed'

        return MultiSwitcher.doStatus(self, maxage)

    def isAllowed(self, pos):
        if self.inRange(pos):
            return True, ''
        else:
            return MultiSwitcher.isAllowed(self, pos)

    def inRange(self, speed):
        return self.customrange[0] < speed < self.customrange[-1]

    def _mapReadValue(self, pos):
        value = MultiSwitcher._mapReadValue(self, pos)
        if value == self.fallback and self.inRange(pos[0]):
            value = pos[0]

        return value

    def doReadCustomrange(self):
        return self._attached_moveables[0].userlimits

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
from nicos.core import status, SIMULATION, dictwith
from nicos.core.params import Attach, Param
from nicos.devices.generic.sequence import SequencerMixin, SeqDev, SeqCall
from nicos.devices.generic.switcher import MultiSwitcher
from nicos.devices.tango import NamedDigitalOutput, VectorInput

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


class Doppler(SequencerMixin, MultiSwitcher):
    """Device to change the dopplerspeed.
    It also compares the speed and amplitude 'seen' by the SIS detector to
    the values set in the doppler and notifies the user if these values do
    not match."""

    parameters ={
        'margins': Param('margin for readout errors in refdevices',
                         dictwith(speed=float, amplitude=float),
                         default=dict(speed=.0, amplitude=.0), settable=True),
        'maxacqdelay': Param('maximum time to wait for the detector to adjust '
                             'when a measurement is started in seconds',
                             int, default=50, settable=True)
    }

    attached_devices = {
        'switch': Attach('The on/off switch of the doppler',
                         NamedDigitalOutput),
        'acq':    Attach('The doppler as seen by the SIS-Detector',
                         AcqDoppler),
    }

    def doRead(self, maxage=0):
        if self._attached_switch.read() == 'off':
            return 0
        return self._mapReadValue(self._readRaw(maxage))

    def _startRaw(self, target):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
            else:
                self._seq_thread.join(0)
            self._seq_thread = None

        cur = self._attached_acq.status()
        if cur == (status.BUSY, 'counting'):
            self.log.warning('Doppler speed can not be changed while '
                             'SIS is counting.')
            return

        seq = list()
        # to change the doppler speed it has to be stopped first
        seq.append(SeqDev(self._attached_switch, 'off'))
        seq.append(SeqCall(session.delay, 3))
        if target[0] != 0:
            seq.append(SeqCall(MultiSwitcher._startRaw, self, target))
            seq.append(SeqDev(self._attached_switch, 'on'))

        seq.append(SeqCall(self.waitForSync, target))

        self._startSequence(seq)

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
        seq_status = SequencerMixin.doStatus(self, maxage)
        if seq_status[0] not in (status.OK, status.WARN):
            return seq_status

        acq_speed, acq_ampl = self._attached_acq.read()
        speed, ampl = self._readRaw()

        if self._attached_switch.read() == 'off':
            if not self.withinMargins(acq_speed, 0, SPEED):
                return (status.WARN, 'detector registers movement of the '
                                     'doppler, although it has been stopped.')

        elif not self.withinMargins(acq_speed, speed, SPEED):
            return (status.WARN, 'doppler and detector do not display matching '
                                 'doppler speeds')
        elif not self.withinMargins(acq_ampl, ampl, AMPLITUDE):
            return (status.WARN, 'doppler and detector do not display matching '
                                 'doppler amplitudes')

        return MultiSwitcher.doStatus(self, maxage)

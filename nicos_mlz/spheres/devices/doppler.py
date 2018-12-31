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
from nicos.core import status
from nicos.core.params import Attach, Param, listof
from nicos.devices.generic.switcher import MultiSwitcher
from nicos.devices.tango import AnalogOutput, NamedDigitalOutput, VectorInput

ELASTIC =   'elastic'
INELASTIC = 'inelastic'


class AcqDoppler(VectorInput):
    '''Doppler values as read by the Detector'''

    parameters ={
        'margins': Param('margin for readout errors in refdevices',
                         listof(float), default=[0,0], settable=True)
    }

    attached_devices = {
        'amplitude': Attach('Referencedevice for amplitude',
                            AnalogOutput),
        'speed':     Attach('Referencedevice for speed',
                            AnalogOutput)
    }

    def init(self):
        VectorInput.init(self)
        self._warning = 0

    def doRead(self, maxage=0):
        speed, ampl = self._dev.getDopplerValues()
        ampl *= 1000

        refspeed = self._attached_speed.read()
        refampl = self._attached_amplitude.read()

        if (speed < refspeed-self.margins[0]
                or speed > refspeed+self.margins[0]
                or ampl < refampl-self.margins[1]
                or ampl > refampl+self.margins[1]):
            self._warning = 1
        else:
            self._warning = 0

        return speed, ampl

    def doStatus(self, maxage=0):
        normal = VectorInput.doStatus(self)
        if normal[0] == status.OK and self._warning:
            return (status.WARN, 'speed and/or amplitude do not '
                                 'align with reference(s)')

        return normal


class Doppler(MultiSwitcher):
    """Device to change the dopplerspeed.
    It also compares the speed and amplitude 'seen' by the SIS detector to
    the values set in the doppler and notifies the user if these values do
    not match."""

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

    def doStart(self, target):
        cur = self.status()
        if cur == (status.BUSY, 'counting'):
            self.log.warning('Doppler speed can not be changed while '
                             'SIS is counting.')
            return

        # to change the doppler speed it has to be stopped first
        self._attached_switch.maw('off')
        session.delay(3)
        if target != 0:
            MultiSwitcher.doStart(self, target)
            self._attached_switch.move('on')

    def doStatus(self, maxage=0):
        doppler = MultiSwitcher.doStatus(self, maxage)
        if doppler[0] == status.OK:
            return self._attached_acq.status()

        return doppler

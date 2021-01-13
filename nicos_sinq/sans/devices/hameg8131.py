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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core import Attach, status
from nicos.core.constants import SIMULATION
from nicos.core.params import oneof
from nicos.devices.epics import EpicsMoveable

from nicos_ess.devices.epics.extensions import EpicsCommandReply


class HAMEG8131(EpicsMoveable):
    """
    This class takes care of initialising the frequency generator,
    and switching it on or off
    """

    attached_devices = {
        'port': Attach('Port to talk directly to the device',
                       EpicsCommandReply),
        'freq': Attach('Flipper frequency',
                       EpicsMoveable),
        'amp': Attach('Flipper amplitude',
                      EpicsMoveable),
    }

    valuetype = oneof('on', 'off')

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        inicommands = ['RM1', 'RFI', 'OT0', 'SW0', 'SK0',
                       'CTM', 'VPP', 'AM0', 'SIN', 'OFS:0E+0',
                       'FRQ:2.534E+5', 'AMP:2.6E+0']
        for com in inicommands:
            self._attached_port.execute(com)

    def doIsAllowed(self, target):
        if target == 'on':
            freq = self._attached_freq.read(0)
            amp = self._attached_amp.read(0)
            if freq < 1. or amp < .1:
                return False,  'Set frequency and amplitude first'
        return True, ''

    def doStart(self, pos):
        if pos == 'on':
            self._put_pv('writepv', 1)
        else:
            self._put_pv('writepv', 0)

    def doRead(self, maxage=0):
        val = self._get_pv('readpv')
        freq = self._attached_freq.read(maxage)
        amp = self._attached_amp.read(maxage)
        if val == 0 or freq < 1. or amp < .1:
            return 'off'
        return 'on'

    def doStatus(self, maxage=0):
        pos = self.doRead(maxage)
        if pos == self.target:
            return status.OK, 'Done'
        return status.BUSY, 'Moving'

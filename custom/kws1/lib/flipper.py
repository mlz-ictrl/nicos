#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Class for controlling the KWS flipper."""

from time import sleep

from nicos.core import HasTimeout, Moveable, Attach, Override, status, oneof, \
    SIMULATION


class Flipper(HasTimeout, Moveable):
    """Controlling the spin flipper.

    Switching the flipper on is done by simultaneously switching a TTL signal
    (via SPS) and switching on the power supply for the flipper box.
    """

    hardware_access = False

    valuetype = oneof('off', 'on')

    attached_devices = {
        'output':  Attach('output bits', Moveable),
        'supply':  Attach('power supply', Moveable),
    }

    parameter_overrides = {
        'fmtstr':   Override(default='%s'),
        'timeout':  Override(default=2),
        'unit':     Override(mandatory=False, default=''),
    }

    def doStatus(self, maxage=0):
        if self._mode == SIMULATION:
            # in simulation mode, we don't know that the current will
            # change when changing the voltage of the power supply
            return status.OK, 'idle'
        flip_bit = self._attached_output.read(maxage)
        current = self._attached_supply.current
        if flip_bit and current > 0.1:
            return status.OK, 'idle'
        if not flip_bit and current < 0.1:
            return status.OK, 'idle'
        return status.WARN, 'inconsistent'

    def doRead(self, maxage=0):
        if self._mode == SIMULATION:
            # in simulation mode, we don't know that the current will
            # change when changing the voltage of the power supply
            return 'on' if self._attached_supply.read(maxage) > 0 else 'off'
        current = self._attached_supply.current
        if current > 0.1:
            return 'on'
        return 'off'

    def doStart(self, target):
        if target == 'on':
            self._attached_supply.start(11.0)
            self._attached_output.start(1)
        else:
            self._attached_output.start(0)
            self._attached_supply.start(0.0)

    def timeoutAction(self):
        self.log.warning('did not reach target, trying again...')
        # The output sometimes seems not to come on.  Therefore,
        # switch it off manually and try again...
        self._attached_output.start(0)
        sleep(1)
        self.start(self.target)

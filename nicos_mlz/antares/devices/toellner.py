#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Simon Sebold <simon.sebold@frm2.tum.de>
#
# *****************************************************************************

"""Special device to amplify an analog output."""
from nicos.core import Attach, HasLimits, Moveable, Param, oneof, status


class ToellnerDc(HasLimits, Moveable):
    """Special device to amplify an analog output."""

    attached_devices = {
        'amplitude': Attach('Amplitude', Moveable),
    }

    parameters = {
        'input_range': Param('Input range',
                             type=oneof('5V', '10V'), settable=True,
                             mandatory=True),
        'max_voltage': Param('Max Voltage',
                             type=float, settable=False, default=20),
        'max_current': Param('Max Current',
                             type=float, settable=False, default=16),
        'mode': Param('current or voltage',
                      type=oneof('current', 'voltage'),
                      settable=False, mandatory=True),
    }

    def doRead(self, maxage=0):
        max_value = self.max_voltage
        if self.mode == 'current':
            max_value = self.max_current

        in_range = 5.
        if self.input_range == '10V':
            in_range = 10.

        ret = float(self._attached_amplitude.read(maxage)) / in_range * max_value
        return ret

    def doStart(self, target):
        max_value = self.max_voltage
        if self.mode == 'current':
            max_value = self.max_current

        in_range = 5.
        if self.input_range == '10V':
            in_range = 10.

        target = float(target) / float(max_value) * in_range

        self._attached_amplitude.start(target)

    def doReadUnit(self):
        if self.mode == 'current':
            return 'A'
        return 'V'

    def doStatus(self, maxage=0):
        if self._attached_amplitude.status(0)[0] == status.DISABLED:
            return status.DISABLED, '%s mode' % self.mode
        return status.OK, '%s mode' % self.mode

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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Moveable, NicosError
from nicos.devices.tango import DigitalOutput


class RefcountDigitalOutput(DigitalOutput):
    def doInit(self, mode):
        self._counter = 0
        # DigitalOutput.doInit(self, mode)

    def doStart(self, target):
        if target:
            self._counter += 1
        else:
            self._counter -= 1
        self._dev.value = self._counter >= 1


class MultiDigitalOutput(Moveable):
    """Writes the same value to multiple digital outputs at once."""

    attached_devices = {
        'outputs': ([DigitalOutput], 'A list of digital outputs to '
                    'switch simultaneously'),
    }

    valuetype = int

    def doStart(self, target):
        for dev in self._adevs['outputs']:
            dev.start(target)

    def doRead(self, maxage=0):
        values = []
        for dev in self._adevs['outputs']:
            values.append(dev.read(maxage))
        if len(set(values)) != 1:
            devnames = [dev.name for dev in self._adevs['outputs']]
            raise NicosError(self,
                'outputs have different read values: '
                + ', '.join('%s=%s' % x for x in zip(devnames, values)))
        return values[0]

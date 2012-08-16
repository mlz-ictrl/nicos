#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""Class for PUMA attenuator consisting of different filter thicknesses."""

__version__ = "$Revision$"

import time

from nicos.core import Moveable, Readable, status, NicosError, PositionError


class Attenuator(Moveable):

    attached_devices = {
        'io_status':  (Readable, 'readout for the current status'),
        'io_set':     (Moveable, 'output to set new value'),
        'io_press':   (Readable, 'input for air pressure (not used)'),
    }

    def doInit(self, mode):
        self._filterlist = [1, 2, 5, 10, 20]

    def doStart(self, position):
        # already there?
        if position == self.read(0):
            return
        # if self.io_press == 0:
        #     raise NicosError('no air pressure; cannot move attenuator')
        # calculate bit pattern to set
        bits = 0
        for i, thick in enumerate(self._filterlist[::-1]):
            if position > thick:
                bits += 1 << i
                position -= thick
        self._adevs['io_set'].move(bits)
        time.sleep(3)
        # check that all filters have arrived
        if self.doStatus()[0] != status.OK:
            raise NicosError('attenuator returned wrong position')
        # print note if desired position is not available
        if position > 0:
            self.log.info('requested filter combination not possible; switched '
                'to %s thickness' % self.format(self.doRead(), unit=True))

    def doReset(self):
        stat1 = self._adevs['io_status'].doRead()
        stat2 = 0
        for i in range(0, 5):
            stat2 += ((stat1 >> (2*i + 1)) & 1) << i
        self._adevs['io_set'].move(stat2)
        self.log.info('device status read from hardware: %s' % stat1)
        self.log.info('device status sent to hardware: %s' % stat2)

    def doRead(self, maxage=0):
        if self.doStatus()[0] != status.OK:
            raise PositionError('device undefined; check it!')
        readvalue = self._adevs['io_status'].read(0.2)
        return sum(self._filterlist[i] for i in range(0, 5)
                   if (readvalue >> (i*2+1)) & 1)

    def doStatus(self, maxage=0):
        stat1 = self._adevs['io_status'].read(maxage)
        stat2 = 0
        stat3 = 0
        for i in range(5):
            stat2 += ((stat1 >> (2*i+1)) & 1) << i
            stat3 += ((stat1 >> (2*i)) & 1) << i
        if (abs(stat1 - stat3) == 0) and stat2 + stat3 == 31:
            return (status.OK, 'idle')
        else:
            return (status.ERROR, 'position undefined, please check')

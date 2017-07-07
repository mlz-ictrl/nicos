#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#    Tobias Weber <tweber@frm2.tum.de>
#
# *****************************************************************************

"""Mira-Stargate.

This is the shielding of the analyzer with 11 blocks.  The att axis does not
move any elements under the blocks, so we can move to a new block state at
any time (in this implementation, before starting the axis).

Only 0, 1 or 2 blocks may be opened at a time.  The first and last block should
not be opened since they are stationary.

The blocks are controlled via a Festo valve arrangement of 11 stable valves
represented by two bits that can be moved into open (01) or closed (10)
positions.

Festo uses Modbus, and the 22 needed output bits are distributed in the lower 8
bits of three consecutive 16-bit holding registers (offset_out).  Readback is
done in three different holding registers with addresses n, n+2, n+4.
"""

from time import time as currenttime

from nicos.core import Param, listof, status, InvalidValueError, Attach
from nicos.devices import tango
from nicos_mlz.mira.axis import HoveringAxis


class Stargate(tango.DigitalOutput):
    """Device for controlling the MIRA-Stargate blocks."""

    valuetype = listof(int)

    parameters = {
        'offset_in':  Param('Offset of digital input values',
                            type=int, mandatory=True),
        'offset_out': Param('Offset of digital output values',
                            type=int, mandatory=True),
        'chevron_att_angles': Param('att angle for shielding elements',
                                    type=listof(listof(int)),
                                    mandatory=True),
    }

    _started = 0

    def doRead(self, maxage=0):
        words = self._dev.ReadOutputWords([self.offset_in, 5])
        bitvals = [words[0], words[2], words[4]]
        chevrons = []

        for bitval in bitvals:
            for _ in range(4):
                chevrons.append(int(bitval & 0b11 == 0b01))
                bitval >>= 2

        return chevrons[:11]

    def doStatus(self, maxage=0):
        if self._started and self._started + 3 > currenttime():
            return status.BUSY, 'moving/waiting'
        return status.OK, ''

    def doStart(self, value):
        bitvals = [0, 0, 0]
        for curidx in range(len(value)):
            curval = value[curidx]

            byteidx = curidx // 4
            bitidx = (curidx % 4) * 2

            if curval:
                bitvals[byteidx] |= (1 << bitidx)
            else:
                bitvals[byteidx] |= (1 << (bitidx+1))

        self._dev.WriteOutputWords([self.offset_out] + bitvals)
        self._started = currenttime()

    def doIsAllowed(self, value):
        if len(value) != 11:
            raise InvalidValueError(self, 'list must have 11 entries')
        # map everything to 0 or 1
        value = [bool(v) for v in value]
        # check allowed positions
        if value == [True] * 11:
            # open everything is allowed
            return True, ''
        if sum(value) > 2:
            return False, 'cannot open more than 2 chevrons'
        if value[0] or value[10]:
            return False, 'cannot open first or last chevron'
        return True, ''

    def doReadFmtstr(self):
        return '[' + ', '.join(['%d'] * 11) + ']'

    def get_chevrons_for_att(self, att):
        chevrons = []

        for curidx in range(len(self.chevron_att_angles)):
            maxmin = self.chevron_att_angles[curidx]

            if(len(maxmin) < 2):
                chevrons.append(0)
                continue

            if(att < maxmin[0] and att > maxmin[1]):
                chevrons.append(1)
            else:
                chevrons.append(0)

        return chevrons


class ATT(HoveringAxis):
    attached_devices = {
        'stargate': Attach('stargate switch device', Stargate),
    }

    parameters = {
        'movestargate': Param('Whether to move the stargate with the axis',
                              type=bool, settable=True, default=True),
    }

    def _preMoveAction(self):
        if self.movestargate:
            self._attached_stargate.start(
                self._attached_stargate.get_chevrons_for_att(self.target))
        else:
            self.log.warning('moving stargate blocks is disabled')
        HoveringAxis._preMoveAction(self)

    def doStatus(self, maxage=0):
        if not self.movestargate:
            return HoveringAxis.doStatus(self, maxage)
        sgstat = self._attached_stargate.status(maxage)
        if sgstat[0] == status.BUSY:
            return status.BUSY, 'stargate moving'
        axstat = HoveringAxis.doStatus(self, maxage)
        if axstat[0] == status.BUSY:
            return axstat
        axvalue = HoveringAxis.doRead(self, maxage)
        chevrons = list(self._attached_stargate.read(maxage))
        if chevrons != self._attached_stargate.get_chevrons_for_att(axvalue):
            return status.ERROR, 'invalid stargate position for att angle'
        return axstat

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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for PUMA PG filter."""

from nicos.core import Moveable, Readable, Param, PositionError, oneof, \
    status, Override, HasTimeout, Attach


class PumaFilter(HasTimeout, Moveable):
    """Class for the PUMA PG filter.

    Components:

    * translation table with pneumatic cylinder
    * 2 limit switches for Position IN/OUT of beam
    * 1 air pressure monitor
    * 1 stepper for rotation of filter
    """

    attached_devices = {
        'motor':     Attach('rotation axis of filter device', Moveable),
        'io_status': Attach('status of the limit switches', Readable),
        'io_set':    Attach('query bit to set filter in/out of beam', Moveable),
        'io_press':  Attach('air pressure status readout', Readable),
    }

    parameters = {
        'material':  Param('Material of filter', type=str, mandatory=True),
        'width':     Param('Width of filter', unit='cm', mandatory=True),
        'height':    Param('Height of filter', unit='cm', mandatory=True),
        'thickness': Param('Thickness of filter', unit='cm', mandatory=True),
        'justpos':   Param('...', mandatory=True),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default=''),
        'timeout':   Override(mandatory=False, default=5),
    }

    valuetype = oneof('in', 'out')

    def doStart(self, position):
        motor = self._attached_motor
        currentpos = self.read(0)
        motorpos = motor.read(0)

        if position == currentpos and motorpos == self.justpos:
            return

        if abs(motorpos - self.justpos) > 0.5:
            motorpos = motor.maw(0)

        self._attached_io_set.start(1 if position == 'in' else 0)
        if self.wait() != position:
            raise PositionError(self, 'device returned wrong position')

        if (self.doStatus()[0] == status.OK) and (motorpos != self.justpos):
            motorpos = motor.maw(self.justpos)
            self.log.info('rotation angle of filter: %s' %
                          motor.format(motorpos, unit=True))

    def doRead(self, maxage=0):
        res = self._attached_io_status.read(maxage)
        if res == 1:
            return 'in'
        elif res == 2:
            return 'out'
        elif res in [0, 3]:
            raise PositionError(self, 'filter unit in error state, somewhere '
                                'in between in/out')
        else:
            raise PositionError(self, 'invalid value of I/O: %s' % res)

    def doStatus(self, maxage=0):
        s1 = self._attached_io_status.read(maxage)
        s2 = self._attached_motor.status(maxage)
        if s1 in [0, 3] or s2[0] == status.BUSY:
            return status.BUSY, 'moving'
        elif s1 in [1, 2] and s2[0] == status.IDLE:
            return status.OK, 'idle'
        else:
            return status.ERROR, 'undefined state'

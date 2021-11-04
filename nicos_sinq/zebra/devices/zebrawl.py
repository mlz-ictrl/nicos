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

from nicos.core.device import Attach, Moveable
from nicos.core.errors import InvalidValueError
from nicos.devices.generic.mono import Monochromator


class ZebraWavelength(Monochromator):
    """
    At Zebra, the wavelength depends on the position of the
    monochromator lift
    """

    attached_devices = {
        'lift': Attach('Monochromator lift device', Moveable)
    }

    def doRead(self, maxage=0):
        pos = self._attached_lift.doRead(maxage)
        posmap = {0: 2.3, 547.45: 1.178}
        for target, wl in posmap.items():
            if abs(target - pos) < 1.:
                return wl
        raise InvalidValueError('Monochromator lift at unknown '
                                'position %f' % pos)

    def doIsAllowed(self, pos):
        return False, 'This monochromator shall not be driven'

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

from nicos.core.device import Attach, Moveable, oneof
from nicos.core.utils import multiStatus
from nicos.devices.generic.mono import Monochromator


class ZebraWavelength(Monochromator):
    """
    At Zebra, the wavelength depends on the position of the
    monochromator lift and the omega value of the monochromator
    """

    attached_devices = {
        'mexz': Attach('Monochromator lift device', Moveable),
        'pg': Attach('PG filter', Moveable),
        'moml': Attach('Lower omega', Moveable),
        'mcvl': Attach('Lower curvature', Moveable),
        'momu': Attach('Upper omega', Moveable),
        'mcvu': Attach('Upper curvature', Moveable),
    }

    _wl_map = {
        1.178: [('mexz', 547.445), ('pg', 'Out'), ('moml', -99.906),
                ('mcvl', 2.2)],
        2.305: [('mexz', .5), ('pg', 'In'), ('momu', -13.152),
                ('mcvu', 158.7)],
        1.383: [('pg', 'Out'), ('mexz', 547.445), ('moml', -35.11),
                ('mcvl', 7)],
        0.778: [('pg', 'Out'), ('mcvl', 2.2), ('mexz', 547.445),
                ('moml', -89.937)]
    }

    _wait_dev = []

    def doRead(self, maxage=0):
        excluded = ['mcvl', 'mcvu']
        for key, data in self._wl_map.items():
            isValid = True
            for entry in data:
                mot, val = entry
                if mot in excluded:
                    continue
                if isinstance(val, float):
                    if not self._adevs[mot].isAtTarget(target=val):
                        isValid = False
                        break
                else:
                    # pgfilter is in or out
                    if self._adevs[mot].read(0) != val:
                        isValid = False
                        break
            if isValid:
                return key
        # self.log.warning('Monochromator in transition or in '
        #                  'in invalid position')
        return -9999.99

    def doInit(self, mode):
        self.valuetype = oneof(*self._wl_map.keys())
        Monochromator.doInit(self, mode)

    def doStart(self, target):
        self._wait_dev = []
        data = self._wl_map[target]
        for entry in data:
            mot, val = entry
            self._adevs[mot].move(val)
            self._wait_dev.append(self._adevs[mot])

    def doStatus(self, maxage=0):
        return multiStatus(self._wait_dev, maxage)

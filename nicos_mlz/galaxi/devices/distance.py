#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI Pilatus detector distance"""

from nicos.core.device import Readable
from nicos.core.params import Param, Attach


class DetectorDistance(Readable):
    """Calculate detector distance from detectortubes position"""

    attached_devices = {
        'detectubes': Attach('Pilatus detector tubes', Readable, multiple=4)
    }

    parameters = {
        'offset': Param('Minimum distance between Pilatus and sample',
                        type=int, settable=True),
    }

    hardware_access = False

    def doInit(self, mode):
        self.log.debug('Detector distance init')
        self.read()

    def doRead(self, maxage=0):
        distance = 0
        for tube in enumerate(self._attached_detectubes, start=2):
            if tube[1].read(maxage) != 'up':
                break
            distance += tube[0] / 2
        return self.offset + distance * 450

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""GALAXI Automatic vacuum control and detector positioning"""

from nicos.core.device import Readable
from nicos.core.params import Attach, Param, listof
from nicos.devices.tango import NamedDigitalOutput


class DetectorDistance(Readable):
    """Calculate detector distance based on the detector tubes position"""

    attached_devices = {
        'detectubes': Attach('Pilatus detector tubes', Readable, multiple=4)
    }

    parameters = {
        'offset': Param('Minimum distance between Pilatus and sample',
                        type=int, settable=True),
        'tubelength': Param('List of tube length',
                            type=listof(int), settable=False,
                            default=[450, 450, 900, 900]),
    }

    hardware_access = False

    def doInit(self, mode):
        self.log.debug('Detector distance init')
        self.read()

    def doRead(self, maxage=0):
        distance = 0
        for tube, l in zip(self._attached_detectubes, self.tubelength):
            # tubes can only be set in correct sequence
            if tube.read(maxage) != 'up':
                break
            distance += l
        return self.offset + distance

class VacuumOperation(NamedDigitalOutput):
    """Provide different vacuum operation states"""

    def doStop(self):
        self._dev.Reset()

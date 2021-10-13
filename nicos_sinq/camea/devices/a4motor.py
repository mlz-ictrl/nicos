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
from nicos.core.device import Attach, Moveable, Param


class CameaA4Motor(Moveable):
    """
    At CAMEA we have this large tank with multiple analysers banks
    each containing in themselves multiple analysers. One of them
    will be selected to provide the counts for counting. Correspondingly
    at CAMEA a4 is the value of the physical motor plus the offset in a4 to
    the selected analyser. This offset comes from a calibration file. We cannot
    use the standard offset for two reasons:
    - The application of the offset needs to be compatible with SICS
    - This a4offset is fixed and comes from the calibration file. We need
    the actual motor offset in order to account for the skewedness of the
    instrument and the sample.
    """

    parameters = {
        'a4offset': Param('Special offset for CAMEA',
                          type=float, settable=True, userparam=True,
                          default=0),
    }

    attached_devices = {
        'rawa4': Attach('Real motor for driving A4', Moveable),
    }

    def doStart(self, target):
        return self._attached_rawa4.doStart(target - self.a4offset)

    def doRead(self, maxage=0):
        return self._attached_rawa4.doRead(maxage) + self.a4offset

    def isAllowed(self, pos):
        return self._attached_rawa4.isAllowed(pos - self.a4offset)

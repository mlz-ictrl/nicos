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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos.core import Param, Override, status
from nicos.core.device import Readable


class ComponentHandler(Readable):
    """
    AMOR component handling module. These distances along the optical bench
    are measured with the dimetix laser distance measurement device.
    To this purpose each component has a little mirror attached to it,
    at a different height for each component. The dimetix is sitting
    on a translation that can be moved up and down and thus can measure
    the distance of a given component by selecting the appropriate height.

    The calculation of distance for each component involves following
    properties:
    - Known offset of the attached mirror to the actual component
    - Offset in the calculation of the distance (occurs when laser is not at 0)
    - Value read from the laser

    The actual value is then given with the following equation:
    S = d - S' -ls
    where d is scale offset, S' is the value read by laser and ls is the
    known offset.

    The mirror height provides the vertical location of the mirror attached
    to the component. If dimetix is at this height then the distance recorded
    is the distance of this component.
    """

    parameters = {
        'markoffset': Param('Known offset to the true value', type=float,
                            default=0.0, mandatory=False, settable=True),
        'scaleoffset': Param('Zero point of the scale', type=float,
                             default=0.0, mandatory=False, settable=True),
        'readvalue': Param('Distance read from the laser', type=float,
                           default=0.0, mandatory=False, settable=True),
        'active': Param('Is this distance currently active', type=bool,
                        default=True, mandatory=False, settable=True),
        'mirrorheight': Param('Vertical height of the attached mirror',
                              type=float, default=1000, mandatory=False,
                              settable=True)
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False, default=(0, 11000)),
        'unit': Override(mandatory=False, default='mm')
    }

    def doRead(self, maxage=0):
        return abs(self.scaleoffset - self.readvalue - self.markoffset)

    def doStatus(self, maxage=0):
        if not self.active:
            return status.OK, 'not active'

        return status.OK, ''

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

""""Manual" moveable devices, to keep track of manual instrument changes."""

__version__ = "$Revision$"

from nicos import status
from nicos.utils import nonemptylistof, anytype
from nicos.device import Moveable, Param, Override, HasLimits
from nicos.errors import InvalidValueError


class ManualMove(HasLimits, Moveable):
    """
    A representation of a manually moveable continuous device.
    """

    def doStart(self, target):
        pass  # self.target has already been set to pos

    def doRead(self):
        return self.target

    def doStatus(self):
        return status.OK, ''


class ManualSwitch(Moveable):
    """
    A representation of a manually changeable device.
    """

    parameters = {
        'states': Param('List of allowed states',
                        type=nonemptylistof(anytype), mandatory=True),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False),
    }

    def doReadTarget(self):
        return self.states[0]

    def doStart(self, target):
        if target not in self.states:
            positions = ', '.join(repr(pos) for pos in self.states)
            raise InvalidValueError(self,
                '%r is an invalid position for this device; '
                'valid positions are %s' % (target, positions))

    def doRead(self):
        return self.target

    def doStatus(self):
        return status.OK, ''

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

""""Manual" moveable devices, to keep track of manual instrument changes."""

__version__ = "$Revision$"

from nicos.core import status, listof, anytype, Moveable, Param, Override, \
     HasLimits, PositionError


class ManualMove(HasLimits, Moveable):
    """A representation of a manually moveable continuous device.

    This device does nothing but record the latest position you moved to.  This
    is useful for instrument parameters that have to be changed manually, but
    you still want to record them in data files, status monitor etc.
    """

    parameters = {
        'default': Param('Default value when freshly initialized'),
    }

    hardware_access = False

    def doReadTarget(self):
        return self.default

    def doStart(self, target):
        pass  # self.target has already been set to position

    def doRead(self):
        return self.target

    def doStatus(self):
        return status.OK, ''


class ManualSwitch(Moveable):
    """A representation of a manually changeable device.

    This is akin to the `ManualMove` device, but for instrument parameters that
    take only discrete values.

    If the `states` parameter is not empty, it represents a list of all allowed
    values of the device.  If it is empty, all values are allowed.
    """

    parameters = {
        'states': Param('List of allowed states',
                        type=listof(anytype), mandatory=True),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False),
    }

    hardware_access = False

    def doReadTarget(self):
        if self.states:
            return self.states[0]

    def doIsAllowed(self, target):
        if self.states and target not in self.states:
            positions = ', '.join(repr(pos) for pos in self.states)
            return False, \
                '%r is an invalid position for this device; ' \
                'valid positions are %s' % (target, positions)
        return True, ''

    def doStart(self, target):
        pass

    def doRead(self):
        if self.target in self.states:
            return self.target
        raise PositionError(self, 'device is in an unknown state')

    def doStatus(self):
        return status.OK, ''

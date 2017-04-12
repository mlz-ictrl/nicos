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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

""""Manual" moveable devices, to keep track of manual instrument changes."""

from nicos.core import status, anytype, nonemptylistof, Moveable, Param, \
    Override, HasLimits, PositionError, oneof


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
        # need not move anything, self.target has already been set to position
        # however, we should update the cache
        self.read()

    def doRead(self, maxage=0):
        return self.target

    def doStatus(self, maxage=0):
        return status.OK, ''


class ManualSwitch(Moveable):
    """A representation of a manually changeable device.

    This is akin to the `ManualMove` device, but for instrument parameters that
    take only discrete values.

    The `states` parameter must be a list of allowed values.
    """

    parameters = {
        'states': Param('List of allowed states',
                        type=nonemptylistof(anytype), mandatory=True),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        self.valuetype = oneof(*self.states)

    def doReadTarget(self):
        #bootstrapping helper
        return self.states[0]

    def doStart(self, target):
        # see ManualMove.doStart
        self.read()

    def doRead(self, maxage=0):
        if self.target in self.states:
            return self.target
        raise PositionError(self, 'device is in an unknown state')

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doIsAllowed(self, target):
        if target in self.states:
            return True, ''
        return False, '%r is not in %r' % (target, self.states)

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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Class for FRM II Helios 3He polarizer operation."""


from nicos.core import Param, Override, usermethod, UsageError
from nicos.devices.tango import NamedDigitalOutput


class HePolarizer(NamedDigitalOutput):
    """
    Class for controlling the polarizing direction of the Helios system.
    """
    parameters = {
        'flippings': Param('Number of Flippings since powerup', volatile=True,
                           unit='', type=int),
    }
    parameter_overrides = {
        'mapping': Override(mandatory=False, default=dict(up=1,down=-1)),
    }

    @usermethod
    def define(self, value):
        """Define the current polarizing direction as 'up' or 'down'."""
        if value not in ['up', 'down']:
            raise UsageError(self, "value must be 'up' or 'down'")
        if self.read(0) != value:
            self._dev.Reverse()
            self.poll()

    def doReadFlippings(self):
        return self._dev.flippings

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""POLI monochromator switcher."""

from nicos.core import Param, NicosError
from nicos.devices.generic.switcher import \
    MultiSwitcher as GenericMultiSwitcher


class MultiSwitcher(GenericMultiSwitcher):
    """MultiSwitcher for the POLI mono."""

    parameters = {
        'changepos': Param('Change position of x_m', mandatory=True),
    }

    def doInit(self, mode):
        GenericMultiSwitcher.doInit(self, mode)
        self._xdev = self._attached_moveables[0]
        if self._xdev.name != 'x_m':
            raise NicosError(self, 'first attached device must be x_m')

    def _startRaw(self, target):
        # always first drive x_m to zero position
        self._xdev.maw(self.changepos)
        # then drive all other axes
        MultiSwitcher._startRaw(self, target)

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

"""Class for Mezei spin flipper."""

__version__ = "$Revision$"

from nicos.core import Moveable, Param, Override, oneof, tupleof, status


class Flipper(Moveable):
    """
    Class for a Mezei flipper consisting of flipper and correction current.
    """

    hardware_access = False

    attached_devices = {
        'flip': (Moveable, 'flipper current'),
        'corr': (Moveable, 'correction current'),
    }

    parameters = {
        'currents': Param('Flipper and correction current', settable=True,
                          type=tupleof(float, float)),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = oneof('on', 'off')

    def doRead(self, maxage=0):
        if abs(self._adevs['flip'].read(maxage)) > 0.05:
            return 'on'
        return 'off'

    def doStart(self, value):
        if value == 'on':
            self._adevs['flip'].start(self.currents[0])
            self._adevs['corr'].start(self.currents[1])
        else:
            self._adevs['flip'].start(0)
            self._adevs['corr'].start(0)

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

    def doWait(self):
        self._adevs['flip'].wait()
        self._adevs['corr'].wait()

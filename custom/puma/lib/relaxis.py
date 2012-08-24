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
#   Peter Link <peter.link@frm2.tum.de>
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for PUMA "relative" axes, i.e. theta/twotheta combinations that are
mounted directly on each other.
"""

__version__ = "$Revision$"

from nicos.core import Moveable


class PumaRelativeAxis(Moveable):

    attached_devices = {
        'mov_ax':      (Moveable, 'moving axis'),
        'relative_ax': (Moveable, 'underlying axis'),
    }

    hardware_access = False

    def doIsAllowed(self, pos):
        realpos = pos - self._adevs['relative_ax'].read(0)
        return self._adevs['mov_ax'].isAllowed(realpos)

    def doStart(self, pos):
        #  first wait that relative axes finished move
        #self.relative_ax.wait()
        realpos = pos - self._adevs['relative_ax'].read(0)
        self._adevs['mov_ax'].start(realpos)

    def doWait(self):
        self._adevs['mov_ax'].wait()

    def doReset(self):
        self._adevs['mov_ax'].reset()

    def doStop(self):
        self._adevs['mov_ax'].stop()

    def doRead(self, maxage=0):
        return self._adevs['mov_ax'].read(maxage) + \
            self._adevs['relative_ax'].read(maxage)

    def doStatus(self, maxage=0):
        return self._adevs['mov_ax'].status(maxage)

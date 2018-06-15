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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# ****************************************************************************

"""Doppler device for SPHERES"""

from nicos.devices.generic.switcher import MultiSwitcher

ELASTIC =   'elastic'
INELASTIC = 'inelastic'


class Doppler(MultiSwitcher):
    def doInit(self, mode):
        MultiSwitcher.doInit(self, mode)

    def _startRaw(self, target):
        MultiSwitcher._startRaw(self, target)

        self._syncronizeImageMode()

    def _syncronizeImageMode(self):
        # when the doppler is not running the measuremode is elastic
        # else inelastic
        if self.read() == 0:
            self._image.setMode(ELASTIC)
        else:
            self._image.setMode(INELASTIC)

    def expectedMode(self):
        if self.read() == 0:
            return ELASTIC
        else:
            return INELASTIC

    def attachImage(self, image):
        self._image = image
        self._syncronizeImageMode()

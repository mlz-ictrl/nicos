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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

"""
This module contains ESS specific EPICS developments.
"""

from nicos.devices.abstract import MappedMoveable
from nicos.devices.epics import EpicsDigitalMoveable


class EpicsMappedMoveable(MappedMoveable, EpicsDigitalMoveable):
    """
    EPICS based implementation of MappedMoveable. Useful for PVs that contain
    enums or bools.
    """

    def doInit(self, mode):
        EpicsDigitalMoveable.doInit(self, mode)
        MappedMoveable.doInit(self, mode)

    def doReadTarget(self):
        target_value = EpicsDigitalMoveable.doReadTarget(self)

        # If this is from EPICS, it needs to be mapped, otherwise not
        if self.targetpv:
            return self._mapReadValue(target_value)

        return target_value

    def _readRaw(self, maxage=0):
        return EpicsDigitalMoveable.doRead(self, maxage)

    def _startRaw(self, target):
        EpicsDigitalMoveable.doStart(self, target)

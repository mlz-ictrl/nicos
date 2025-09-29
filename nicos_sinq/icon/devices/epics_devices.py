# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core import status
from nicos.devices.epics.pyepics import \
    EpicsDigitalMoveable as EpicsCoreDigitalMoveable, \
    EpicsReadable as EpicsCoreReadable


class EpicsDigitalMoveable(EpicsCoreDigitalMoveable):
    """
    This adds a doStatus() Method to the core
    EpicsDigitalMoveable
    """
    def doStatus(self, maxage=0):
        return status.OK, 'Idle'


class EpicsReadable(EpicsCoreReadable):
    def doStatus(self, maxage=0):
        return status.OK, 'Idle'

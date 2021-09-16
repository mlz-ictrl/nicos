#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

from nicos.core import status

SEVERITY_TO_STATUS = {
    0: status.OK,  # NO_ALARM
    1: status.WARN,  # MINOR
    2: status.ERROR,  # MAJOR
    3: status.UNKNOWN,  # INVALID
}

STAT_TO_STATUS = {
    0: status.OK,  # OK
    9: status.ERROR,  # Communication error
    17: status.UNKNOWN,  # Invalid/unknown IOC state
}

from nicos.devices.epics.monitor import PyEpicsMonitor as PVMonitor
from nicos.devices.epics.pyepics import EpicsAnalogMoveable, EpicsDevice, \
    EpicsDigitalMoveable, EpicsMoveable, EpicsReadable, EpicsStringMoveable, \
    EpicsStringReadable, EpicsWindowTimeoutDevice, pvget, pvput

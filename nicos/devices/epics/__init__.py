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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import

import os

from nicos.core import status

SEVERITY_TO_STATUS = {
    0: status.OK,  # NO_ALARM
    1: status.WARN,  # MINOR
    2: status.ERROR,  # MAJOR
}

STAT_TO_STATUS = {
    0: status.OK,  # OK
    9: status.ERROR,  # Communication error
    17: status.UNKNOWN,  # Invalid/unknown IOC state
}

# Use environment variable to determine which python EPICS
# binding it to be used
if os.environ.get('NICOS_EPICS') == 'pvaccess':
    from nicos.devices.epics.pvaccess import EpicsDevice, EpicsReadable, \
        EpicsStringReadable, EpicsMoveable, EpicsAnalogMoveable, \
        EpicsDigitalMoveable, EpicsWindowTimeoutDevice
else:
    from nicos.devices.epics.pyepics import EpicsDevice, EpicsReadable, \
        EpicsStringReadable, EpicsMoveable, EpicsAnalogMoveable, \
        EpicsDigitalMoveable, EpicsWindowTimeoutDevice

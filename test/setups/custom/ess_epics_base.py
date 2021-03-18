# -*- coding: utf-8 -*-
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

devices = dict(
    DeviceReadable = device('nicos.devices.epics.pyepics.EpicsReadable',
        description = 'Simple readable device',
        readpv = 'TEST:read',
        unit = '',
    ),
    DeviceMoveable = device('nicos.devices.epics.pyepics.EpicsMoveable',
        description = 'Simple moveable device',
        readpv = 'TEST:read',
        writepv = 'TEST:write',
        unit = '',
    ),
    DeviceMoveableWithTarget = device('nicos.devices.epics.pyepics.EpicsMoveable',
        description = 'Simple moveable device',
        readpv = 'TEST:read',
        writepv = 'TEST:write',
        targetpv = 'TEST:target',
        unit = '',
    ),
)

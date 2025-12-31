# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************
name = 'SINQ logical motors'

includes = ['stdsystem']

description = 'Test setup for SINQ logical motors using the EIGER A2 example'

devices = dict(
    d2l = device('nicos.devices.generic.VirtualMotor',
        unit = 'degree',
        description = 'Left slit block',
        abslimits = (-100, 0),
        precision = 0.01,
        curvalue = -52.5,
    ),
    d2r = device('nicos.devices.generic.VirtualMotor',
        unit = 'degree',
        description = 'Right slit block',
        abslimits = (-100, 0),
        precision = 0.01,
        curvalue = -42.5,
    ),
    a2rot = device('nicos.devices.generic.VirtualMotor',
        unit = 'degree',
        description = 'Left slit block',
        abslimits = (16, 90),
        precision = 0.01,
        curvalue = 44.,
    ),
    a2controller = device('nicos_sinq.eiger.devices.eigermono.EigerA2Controller',
        description = 'Controller for aligning A2 and A2 slits',
        reala2 = 'a2rot',
        left = 'd2l',
        right = 'd2r',
        visibility = (),
    ),
    a2 = device('nicos_sinq.devices.logical_motor.LogicalMotor',
        description = 'Logical A2 motor',
        controller = 'a2controller',
        abslimits = (16, 90.14)
    ),
    a2w = device('nicos_sinq.devices.logical_motor.LogicalMotor',
        description = 'Logical out slit width',
        controller = 'a2controller',
        abslimits = (0, 20.)
    ),
)

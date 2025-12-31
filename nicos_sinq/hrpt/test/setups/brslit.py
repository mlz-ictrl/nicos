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
name = 'SINQ HRPT BRslit'

includes = ['stdsystem']

description = 'Test setup for the HRPT brslit'

devices = dict(
    brle = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        description = 'Left blade',
        abslimits = (-16, 1.5),
        precision = 0.01,
    ),
    brri = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        description = 'Right blade',
        abslimits = (-16, 1.5),
        precision = 0.01,
    ),
    brto = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        description = 'Top blade',
        abslimits = (-44, 1.5),
        precision = 0.01,
    ),
    brbo = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        description = 'Bottom blade',
        abslimits = (-48, 1.5),
        precision = 0.01,
    ),
    slit = device('nicos_sinq.hrpt.devices.brslit.BRSlit',
        description = 'Slit 2 with left, right, bottom and top motors',
        left = 'brle',
        top = 'brto',
        bottom = 'brbo',
        right = 'brri',
        visibility = (),
    ),
)

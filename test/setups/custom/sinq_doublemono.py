# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
name = 'SINQ Double Monochromator'

includes = ['stdsystem']

description = 'Test setup for the SINQ double monochromator'

devices = dict(
    mth1 = device('nicos.devices.generic.VirtualMotor',
        unit = 'degree',
        description = 'First blade rotation',
        abslimits = (-180, 180),
        precision = 0.01
    ),
    mth2 = device('nicos.devices.generic.VirtualMotor',
        unit = 'degree',
        description = 'Second blade rotation',
        abslimits = (-180, 180),
        precision = 0.01
    ),
    mtx = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        description = 'Blade translation',
        abslimits = (-1000, 1000),
        precision = 0.01
    ),
    wavelength = device('nicos_sinq.devices.doublemono.DoubleMonochromator',
        description = 'SINQ Double Monochromator',
        unit = 'A',
        safe_position = 20.,
        dvalue = 3.335,
        distance = 100.,
        abslimits = (2.4, 6.2),
        mth1 = 'mth1',
        mth2 = 'mth2',
        mtx = 'mtx'
    ),
)

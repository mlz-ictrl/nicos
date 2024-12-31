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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

name = 'test_moke01 setup'

devices = {
    'MagB': device('nicos_jcns.moke01.devices.moke.MokeMagnet',
        intensity = 'Intensity',
        magsensor = 'Mag_sensor',
        currentsource = 'PS_current',
        maxramp = 400.0,
        ramp = 400.0,
        fmtstr = '%.6f',
    ),
    'Intensity': device('test.nicos_jcns.moke01.utils.VirtualSensor',
        unit = 'V',
        curvalue = 1,
        abslimits = (0, 3),
        speed = 0,
        ramp = 0,
    ),
    'Mag_sensor': device('test.nicos_jcns.moke01.utils.VirtualSensor',
        unit = 'T',
        curvalue = 0,
        abslimits = (-400, 400),
        speed = 0,
        ramp = 0,
    ),
    'PS_current': device('test.nicos_jcns.moke01.utils.VirtualPS',
        unit = 'A',
        curvalue = 0,
        abslimits = (-400, 400),
        speed = 0,
        ramp = 400.0,
    ),
}

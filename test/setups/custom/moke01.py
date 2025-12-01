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

from nicos.utils.functioncurves import Curves
from nicos_jcns.moke01.utils import generate_intvb

devices = {
    'MagB': device('nicos_jcns.moke01.devices.virtual.VirtualMokeMagnet',
        unit = 'mT',
        intensity = 'Intensity',
        magsensor = 'Mag_sensor',
        currentsource = 'PS_current',
        calibration = {
            'stepwise': {
                '10000.0':
                    Curves([[(-1000, -1000), (-250, -750), (300, 750), (1000, 1000)],
                            [(1000, 1000), (250, 750), (-300, -750), (-1000, -1000)]])
            },
            'continuous': {
            },
        },
        ramp = 1e4,
        maxramp = 1e6,
        pollinterval = 0.5,
        fmtstr = '%.3f',
    ),
    'Intensity': device('nicos_jcns.moke01.devices.virtual.VirtualMokeSensor',
        mappeddevice = 'Mag_sensor',
        unit = 'V',
        valuemap = generate_intvb(-1000, 1000),
        error = 0.02,
        pollinterval = 0.5,
    ),
    'Mag_sensor': device('nicos_jcns.moke01.devices.virtual.VirtualMokeSensor',
        mappeddevice = 'PS_current',
        unit = 'mT',
        valuemap = Curves([[(-1000, -1000), (-250, -750), (300, 750), (1000, 1000)],
                           [(1000, 1000), (250, 750), (-300, -750), (-1000, -1000)]]),
        error = 0.01,
        pollinterval = 0.5,
    ),
    'PS_current': device('nicos_jcns.moke01.devices.virtual.VirtualPowerSupply',
        unit = 'A',
        abslimits = (-1000, 1000),
        ramp = 1e4,
        maxramp = 1e6,
        fmtstr = '%.1f',
    ),
}

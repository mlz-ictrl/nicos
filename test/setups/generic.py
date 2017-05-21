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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

name = 'test_generic setup'

includes = ['stdsystem', 'detector']

devices = dict(
    v1 = device('devices.generic.VirtualMotor',
        abslimits = (0, 5),
        unit = 'mm',
        speed = 1.5
    ),
    v2 = device('devices.generic.ManualSwitch',
        states = ['up', 'down'],
    ),
    v3 = device('devices.generic.VirtualMotor',
        abslimits = (0, 10),
        unit = 'mm',
        speed = 0,
    ),
    m1 = device('devices.generic.ManualSwitch',
        states = ['up', 'down'],
    ),
    # m2 = device('devices.generic.ManualSwitch',
    #     states = [],
    # ),
    m3 = device('devices.generic.ManualSwitch',
        states = ['up', 'down'],
        target = 'inbetween',
    ),
    m4 = device('devices.generic.ManualMove',
        abslimits = (0, 100),
        unit = 'mm',
    ),
    sw = device('devices.generic.Switcher',
        moveable = 'v3',
        mapping = {'left': 1.,
                   'right': 3.,
                   'outside': 1000.},
        precision = 0.05,
    ),
    sw2 = device('devices.generic.Switcher',
        moveable = 'v3',
        mapping = {'left': 1.,
                   'right': 3.,
                   'outside': 1000.},
        precision = 0.0,
        blockingmove = False,
    ),
    rsw = device('devices.generic.ReadonlySwitcher',
        readable = 'v3',
        mapping = {'left': 1.,
                   'right': 3.},
        precision = 0.05,
    ),
    rsw2 = device('devices.generic.ReadonlySwitcher',
        readable = 'v3',
        mapping = {'left': 1.,
                   'right': 3.},
        precision = 0.0,
    ),
    swfb = device('devices.generic.Switcher',
        moveable = 'v3',
        mapping = {'left': 1.,
                   'right': 3.,
                   'outside': 1000.},
        precision = 0.05,
        fallback = 'unknown',
    ),
    rswfb = device('devices.generic.ReadonlySwitcher',
        readable = 'v3',
        mapping = {'left': 1.,
                   'right': 3.},
        precision = 0.0,
        fallback = 'unknown',
    ),
    aliasDev = device('devices.generic.DeviceAlias',
        alias = '',
    ),
    paramdev = device('devices.generic.ParamDevice',
        device = 'v1',
        parameter = 'speed',
    ),
    freespace = device('devices.generic.FreeSpace',
        path = '/',
    ),
    freespace2 = device('devices.generic.FreeSpace',
        path = '/verystrangepath',
    ),
    scandet = device('devices.generic.ScanningDetector',
        description = 'Generic scanning detector',
        scandev = 'v1',
        positions = [1.0, 2.0, 3.0],
        detector = 'det'
    ),
)

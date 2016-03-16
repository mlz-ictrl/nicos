#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

includes = ['stdsystem']

devices = dict(
    v1 = device('nicos.devices.generic.VirtualMotor',
                abslimits = (0, 5),
                unit = 'mm',
                speed = 1.5
               ),
    v2 = device('nicos.devices.generic.ManualSwitch',
                states = ['up', 'down'],
               ),
    v3 = device('nicos.devices.generic.VirtualMotor',
                abslimits = (0, 10),
                unit = 'mm',
                speed = 0,
               ),
    m1 = device('nicos.devices.generic.ManualSwitch',
                states = ['up', 'down']
               ),
    m2 = device('nicos.devices.generic.ManualSwitch',
                states = [],
               ),
    m3 = device('nicos.devices.generic.ManualSwitch',
                states = ['up', 'down'],
                target = 'inbetween',
               ),
    sw = device('nicos.devices.generic.Switcher',
                moveable = 'v3',
                mapping = {'left': 1., 'right': 3., 'outside': 1000.},
                precision = 0.05,
               ),
    sw2 = device('nicos.devices.generic.Switcher',
                 moveable = 'v3',
                 mapping = {'left': 1., 'right': 3., 'outside': 1000.},
                 precision = 0.0,
                 blockingmove = False,
                ),
    rsw = device('nicos.devices.generic.ReadonlySwitcher',
                 readable = 'v3',
                 mapping = {'left': 1., 'right': 3.},
                 precision = 0.05,
                ),
    rsw2 = device('nicos.devices.generic.ReadonlySwitcher',
                 readable = 'v3',
                 mapping = {'left': 1., 'right': 3.},
                 precision = 0.0,
                ),
    swfb = device('nicos.devices.generic.Switcher',
                  moveable = 'v3',
                  mapping = {'left': 1., 'right': 3., 'outside': 1000.},
                  precision = 0.05,
                  fallback = 'unknown',
                 ),
    rswfb = device('nicos.devices.generic.ReadonlySwitcher',
                   readable = 'v3',
                   mapping = {'left': 1., 'right': 3.},
                   precision = 0.0,
                   fallback = 'unknown',
                  ),
    aliasDev = device('nicos.devices.generic.DeviceAlias',
                      alias = '',
                     ),
    paramdev = device('nicos.devices.generic.ParamDevice',
                      device = 'v1',
                      parameter = 'speed',
                     ),
    freespace = device('devices.generic.FreeSpace',
                       path = '/',
                       ),
    freespace2 = device('devices.generic.FreeSpace',
                       path = '/verystrangepath',
                       ),
)

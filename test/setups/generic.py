#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

includes = ['system']

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
    sw = device('nicos.devices.generic.Switcher',
                moveable = 'v3',
                states = ['left', 'right', 'outside'],
                values = [1., 3., 1000.],
                precision = 0.05,
               ),
    broken_sw = device('nicos.devices.generic.Switcher',
                       states = ['0', '10', '20'],
                       values = [0, 10],
                       precision = 0,
                       moveable = 'v3'
                      ),
    rsw = device('nicos.devices.generic.ReadonlySwitcher',
                 readable = 'v3',
                 states = ['left', 'right'],
                 values = [1., 3.],
                 precision = 0.05,
                ),
    aliasDev = device('nicos.devices.generic.DeviceAlias',
                      alias = '',
                     ),
    paramdev = device('nicos.devices.generic.ParamDevice',
                      device = 'v1',
                      parameter = 'speed',
                     ),
)

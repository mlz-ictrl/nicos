#  -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

name = 'test_antares setup'

devices = dict(
    mono = device('nicos_mlz.antares.devices.monochromator.Monochromator',
        dvalue1 = 3.354,
        dvalue2 = 3.354,
        distance = 97,
        phi1 = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            curvalue = 12,
            abslimits = (12, 66),
        ),
        phi2 = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            curvalue = 12,
            abslimits = (12, 66),
        ),
        translation = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            curvalue = --50,
            abslimits = (-120, 260),
        ),
        inout = device('nicos.devices.generic.Switcher',
            moveable = device('nicos.devices.generic.ManualSwitch',
                states = [1, 2],
            ),
            mapping = {'in': 1,
                       'out': 2},
            fallback = '<undefined>',
            unit = '',
            precision = 0,
        ),
        abslimits = (1.4, 6.0),
        userlimits = (1.4, 6.0),
        warnlimits = (1.5, 5.9),
        maxage = 5,
        pollinterval = 3,
        parkingpos = {
            'phi1': 12,
            'phi2': 12,
            'translation': -50,
            'inout': 'out'
        },
    ),
)

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

description = 'test_multiswitch setup'

includes = ['stdsystem']

devices = dict(
    x = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        fmtstr = '%.2f',
        abslimits = (0, 600),
        jitter = 0.02,
        unit = 'mm',
    ),
    x_sw = device('nicos.devices.generic.Switcher',
        moveable = 'x',
        mapping = {'1': 594.5,
                   '2': 535.5,
                   '3': 476.5,
                   '4': -100},
        precision = 0.05,
        blockingmove = False,
    ),
    y = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        fmtstr = '%.2f',
        abslimits = (-50, 50),
        jitter = 0.02,
        unit = 'mm',
    ),
    y_sw = device('nicos.devices.generic.Switcher',
        moveable = 'y',
        mapping = {'top': 28.,
                   'bottom': -31.0},
        precision = 0.05,
        blockingmove = False,
    ),
    sc1 = device('nicos.devices.generic.MultiSwitcher',
        moveables = ['x', 'y'],
        mapping = {
            '1': [594.5, -31],
            '2': [535.5, -31],
            '3': [476.5, -31],
            '4': [417.5, -31],
            'outside': [-55., 28],
        },
        precision = [0.05],
        blockingmove = False,
    ),
    sc2 = device('nicos.devices.generic.MultiSwitcher',
        moveables = ['x_sw', 'y_sw'],
        mapping = {
            '1': ['1', 'bottom'],
            '2': ['2', 'bottom'],
            '3': ['3', 'top'],
            'outside': ['4', 'top'],
        },
        precision = None,
        blockingmove = False,
    ),
    msw3 = device('nicos.devices.generic.MultiSwitcher',
        moveables = ['x', 'y', 'x'],
        mapping = {'1': [1, 0, 1]},
        precision = [0.05, 0.01]
    ),
    msw4 = device('nicos.devices.generic.MultiSwitcher',
        moveables = ['x', 'y', 'x'],
        mapping = {'1': [1, 0]},
        precision = [0.05, 0.01, 0.05]
    ),
    msw5 = device('nicos.devices.generic.MultiSwitcher',
        moveables = ['x', 'y', 'x'],
        mapping = {'1': [1, 0, 1],
                   '2': [0, 1, 0]},
        precision = [0.05, None, 0.05]
    ),
    mswfb = device('nicos.devices.generic.MultiSwitcher',
        moveables = ['x', 'y', 'x'],
        mapping = {'1': [1, 0, 1]},
        precision = [0.05, 0.01, 0.0],
        fallback = 'unknown',
    ),
)

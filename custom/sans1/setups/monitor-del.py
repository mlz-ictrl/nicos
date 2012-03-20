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

description = 'setup for the status monitor for SANS1'
group = 'special'

_interfaceboxtop = (
    'Interface Box (top)',
    [
        [
            {'name' : 'Humidity',    'dev': 'tub_h1', 'min': 0, 'max': 30},
            {'name' : 'Temperature', 'dev': 'tub_t6', 'max' : 30, },
        ],
    ],
#
# Only used if a master has this setup loaded, if missed it will be used 
# unconditionally
#
#   'tube_environment',
)

_interfaceboxbottom = (
    'Interface Box (bottom)',
    [
        [
            {'name' : 'Humidity',    'dev': 'tub_h2', 'min': 0, 'max': 30},
            {'name' : 'Temperature', 'dev': 'tub_t7', 'max' : 30,},
        ],
    ],
#   'tube_environment',
)

_nim_voltage = (
    'Voltage Detector NIM',
    [
        [
            {'name' : '+', 'dev' : 'tub_v1',},
            {'name' : '-', 'dev' : 'tub_v2',},
        ],
    ],
#   'tube_environment',
)

_electronicsbox = (
    'Temperature Electronics Box',
    [
         [
             {'name' : 'left',   'dev' : 'tub_t1', 'max' : 40,},
             {'name' : 'middle', 'dev' : 'tub_t2', 'max' : 40,},
             {'name' : 'right',  'dev' : 'tub_t3', 'max' : 40,},
         ],
    ],
#   'tube_environment',
)

_pressureblock = (
    'Pressure',
    [
        [
            {'name': 'P1', 'dev': 'tub_p1'},
            {'name': 'P2', 'dev': 'tub_p2'},
            {'name': 'P3', 'dev': 'tub_p3'},
        ],
    ],
#   'tube_environment',
)

_warnings = [
    ('tub_t1/value', '> 35', 'Temp in electronics box > 35'),
    ('tub_t2/value', '> 35', 'Temp in electronics box > 35'),
    ('tub_t3/value', '> 35', 'Temp in electronics box > 35'),
]

_rightcolumn = [
    _nim_voltage,
    _electronicsbox,
]

_leftcolumn = [
    _pressureblock,
    _interfaceboxtop,
    _interfaceboxbottom,
]

devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'SANS1 status monitor',
                     loglevel = 'info',
                     server = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 16,
                     padding = 5,
                     layout = [
#                                  [_expcolumn], 
                                  [_leftcolumn, _rightcolumn, ]
                              ],
                     warnings = _warnings,
                     notifiers = [])
)

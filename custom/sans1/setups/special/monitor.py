#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

_ = dict

_pressuretube = (
    'Pressure Tube',
    [
        [
            _( name='Nose', dev='p_t_nose'),
            _( name='Tube', dev='p_t_tube'),
        ],
    ],
   #~ 'tube_environment',
)

_pressurecoll = (
    'Pressure Collimation',
    [
        [
            _( name='Pump', dev='p_c_pump'),
            _( name='Tube', dev='p_c_tube'),
            _( name='Nose', dev='p_c_nose'),
        ],
    ],
)

_table = (
    'Sample Table',
    [
        [
            _( name='z-2a', dev='z_2a'),
        ],
        [
            _(name='y-2a', dev='y_2a'),
        ],
        [
            _(name='x-2a', dev='x_2a'),
        ],
        [
            _(name='phi-2b', dev='phi_2b'),
        ],
        [
            _(name='chi-2b', dev='chi_2b'),
        ],
        [
            _(name='omega-2b', dev='omega_2b'),
        ],
        [
            _(name='z-2b', dev='z_2b'),
        ],
        [
            _(name='y-2b', dev='y_2b'),
        ],
        [
            _(name='x-2b', dev='x_2b'),
        ],
    ],
)

_sans1magnet = (
    'Sans1Magnet',
    [
        [
            _(name='Left Coil', dev='b_left'),
            _(name='Right Coil', dev='b_right'),
            _(name='Field', dev='b_overall'),
        ]
    ],
    'magnet_sans1'
)

_htf02 = (
    'HTF02',
    [
        [
            _(name='Temperature', dev='t_htf02'),
        ]
    ],
    'magnet_sans1'
)

_sans1detector = (
    'Detector',
    [
        [
            _(name='Voltage',dev='hv'),#,width=8),
            _(name='omega-1a',dev='det1_omega1a'),
        ],
        [
            _(name='x-1a',dev='det1_x1a'),
            _(name='z-1a',dev='det1_z1a'),
        ],
    ]
)


_warnings = [
]

devices = dict(
    #~ Monitor = device('nicos.monitor.qt.Monitor',
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'SANS-1 status monitor',
                     loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 3,
                     layout = [
                                  [[_table,], [_pressurecoll,_sans1detector], [_sans1magnet], [_htf02], [_pressuretube,],]
                              ],
                    )
)

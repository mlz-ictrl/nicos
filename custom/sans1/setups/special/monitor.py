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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'setup for the status monitor for SANS1'
group = 'special'

_ = dict

_pressuretube = (
    'Pressure Tube',
    [
        [
            _( name='Nose', dev='tub_p2'),
            _( name='Tube', dev='tub_p1'),
        ],
    ],
   #~ 'tube_environment',
)

_pressurecoll = (
    'Pressure Collimation',
    [
        [
            _( name='Pump', dev='coll_p3'),
            _( name='Tube', dev='coll_p1'),
            _( name='Nose', dev='coll_p2'),
        ],
    ],
)

_lengthcoll = (
    'Collimation length',
    [
        [
            _( name='length', dev='col'),
        ],
    ],
)

_sc1 = (
    'Sample Changer 1',
    [
        [
            _( name='Position', dev='sc1_sw'),
        ], [
            _( name='sc1', dev='sc1'),
        ],
    ],
)

_table = (
    'Sample Table',
    [
        [
            _( name='z-2a', dev='z_2a'),
         ], [
            _(name='y-2a', dev='y_2a'),
         ], [
            _(name='x-2a', dev='x_2a'),
        ], [
            _(name='phi-2b', dev='phi_2b'),
         ], [
            _(name='chi-2b', dev='chi_2b'),
         ], [
            _(name='omega-2b', dev='omega_2b'),
        ], [
            _(name='y-2b', dev='y_2b'),
         ], [
            _(name='z-2b', dev='z_2b'),
         ], [
            _(name='x-2b', dev='x_2b'),
        ],
    ],
)

_sans1magnet = (
    'Sans1Magnet',
    [
        [
            _(name='Field', dev='b_overall'),
         ], [
            _(name='Power Supply 1', dev='b_left'),
            _(name='Power Supply 2', dev='b_right'),
        ]
    ],
)

_newport02 = (
    'NewPort 02',
    [
        [
            _(name='position', dev='sth_newport02'),
         ],
    ],
)

_ccr10 = (
    'CCR10',
    [
        [
            _( name='Setpoint', key='t/setpoint', unitkey='t/unit',),
            ], [
            _( name='A', dev='T_ccr10_A'),
            _( name='B', dev='T_ccr10_B'),
        ],
    ],
)

_ccr11 = (
    'CCR11',
    [
        [
            _( name='Setpoint', key='t/setpoint', unitkey='t/unit',),
            ], [
            _( name='A', dev='T_ccr11_A'),
            _( name='B', dev='T_ccr11_B'),
            ], [
            _( name='C', dev='T_ccr11_C'),
            _( name='D', dev='T_ccr11_D'),
        ],
    ],
)


_ccr12 = (
    'CCR12',
    [
        [
            _( name='Setpoint', key='t/setpoint', unitkey='t/unit',),
            ], [
            _( name='A', dev='T_ccr12_A'),
            _( name='B', dev='T_ccr12_B'),
        ],
    ],
)

_htf03 = (
    'HTF03',
    [
        [
               _(name='Temperature', dev='t_htf03'),
        ]
    ],
#    'magnet_sans1'
)

_spinflipper = (
    'Spin Flipper',
    [
        [
            _(name='Power', dev='p_sf'),
            _(name='Frequency', dev='f_sf'),
         ], [
            _(name='Forward', dev='forward_sf'),
            _(name='Reverse', dev='reverse_sf'),
         ], [
            _(name='Temperature of AG1016', dev='t_sf'),
         ], [
            _(name='Ampl HP33220a', dev='a_agilent1'),
            _(name='Freq HP33220a', dev='f_agilent1'),
        ]
    ],
#    'magnet_sans1'
)

_sans1detector = (
    'Detector',
    [
        [
            _(name='t', dev='det1_t_ist'),
            _(name='t set', dev='det1_t_soll'),
        ], [
            _(name='Voltage',dev='hv'),#,width=8),
            _(name='det1_z-1a',dev='det1_z1a'),
        ], [
            _(name='det1_omg-1a',dev='det1_omega1a'),
            _(name='det1_x-1a',dev='det1_x1a'),
        ], [
            _(name='bs1_x-1a',dev='bs1_x1a'),
            _(name='bs1_y-1a',dev='bs1_y1a'),
        ]
    ]
)

_sans1sel = (
    'Selector',
    [
        [
            _( name='sel-ng', dev='sel_ng_sw'),
         #], [
         #   _( name='sel-ng', dev='sel_ng'),
        ], [
            _(name='sel-tilt', dev='sel_tilt'),
        ]
    ],
)

_sans1general = (
    'General',
    [
        [
            _(name='Reactor', dev='ReactorPower'),
            _(name='6 Fold Shutter', dev='Sixfold'),
            _(name='NL4a', dev='NL4a'),
        ], [
            _(name='T in', dev='t_in_memograph'),
            _(name='T out', dev='t_out_memograph'),
            _(name='Cooling', dev='cooling_memograph'),
        ], [
            _(name='Flow in', dev='flow_in_memograph'),
            _(name='Flow out', dev='flow_out_memograph'),
            _(name='Leakage', dev='leak_memograph'),
        ], [
            _(name='Pressure in', dev='p_in_memograph'),
            _(name='Pressure out', dev='p_out_memograph'),
        ], [
            _(name='Crane Pos', dev='Crane'),
            _(name='FAK 40 Cap', dev='FAK40_Cap'),
            _(name='FAK 40 Pres', dev='FAK40_Press'),
        ]
    ],
#    'magnet_sans1'
)



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
                                [
                                  [_sans1sel,],
                                  [_pressurecoll,_lengthcoll,_sans1detector,_sans1general],
                                  [_sc1,_table,],
                                  [_htf03,_spinflipper,_sans1magnet,_newport02],
                                  [_pressuretube,_ccr10,_ccr11,_ccr12],
                                ],
                              ],
                    )
)

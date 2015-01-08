#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

_pressuretube = (
    'Pressure Tube',
    [
        [
            {'name': 'Tube', 'dev': 'tub_p1'},
            {'name': 'Nose', 'dev': 'tub_p2'},
#            {'name': 'P3', 'dev': 'tub_p3'},
        ],
    ],
#   'tube_environment',
)

_pressurecoll = (
    'Pressure Collimation',
    [
        [
            {'name' : 'Tube', 'dev' : 'coll_p1'},
            {'name' : 'Nose', 'dev' : 'coll_p2'},
            {'name' : 'Pump', 'dev' : 'coll_p2'},
        ],
    ],
)

_leftcolumn = [
    _pressuretube,
]

_rightcolumn = [
    _pressurecoll,
]

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'SANS1 status monitor',
                     loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 16,
                     padding = 5,
                     layout = [
                                  [[_pressuretube,], [_pressurecoll,], ]
#                                  [_leftcolumn, _rightcolumn, ]
                              ],
                    ),
)

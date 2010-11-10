#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS monitor setup file with a few devices
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

name = 'setup for the status monitor'
group = 'special'

_row_filter1 = [
    {'name': 'a1', 'key': 'a1/value', 'unit': 'deg'},
    {'name': 'm1', 'key': 'm1/value'},
    {'name': 'c1', 'key': 'c1/value'},
]

_row_filter2 = [
    {'name': 'timer', 'key': 'timer/value'},
    {'name': 'ctr1', 'key': 'ctr1/value', 'unit': 'cts'},
    {'name': 'ctr2', 'key': 'ctr2/value'},
]

_block1 = ('Test devices', [_row_filter1, _row_filter2])

_column1 = [
    _block1,
    #_block2,
    #_block3,
]

_column2 = [
    #_block4,
    #_block5,
    #_block6,
]

_layout = [
    _column1,
    #_column2,
]

devices = dict(
    Monitor = device('nicm.monitor.Monitor',
                     title='Status monitor',
                     loglevel='debug',
                     server='localhost:14869',
                     prefix='nicm/',
                     font='Luxi Sans',
                     valuefont='Consolas',
                     layout=_layout)
)

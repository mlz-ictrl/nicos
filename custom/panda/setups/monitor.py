#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id: monitor.py 350 2011-02-23 14:22:04Z gbrandl $
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

description = 'setup for the status monitor'
group = 'special'

_exp = [('Experiment', [[{'key': 'exp/proposal', 'name': 'Proposal'},
                          {'key': 'exp/title', 'name': 'Title', 'istext': True, 'width':40},
                          {'key': 'filesink/lastfilenumber', 'name': 'Last file number'}]])]

_row1 = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']

_row2 = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8']

_row3 = ['p1',  'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']

_r=[{'key': 'exp/proposal', 'name': 'Proposal'},
                          {'key': 'exp/title', 'name': 'Title', 'istext': True, 'width': 80},
                          {'key': 'filesink/lastfilenumber', 'name': 'Last file number'}]


_block1 = ('Motorrahmen Test', [_row1, _row2, _row3], 'testaxes')
_block2 = ('Panda S7', [['s7coder','s7motor','mtt']], 'panda_s7')

_eblock = ('Experiment', [_r])

_column1 = [
    _eblock,
    _block1,
    _block2,
    #_block1,
    #_block3,
]

devices = dict(
    Monitor = device('nicos.monitor.fl.Monitor',
                     title = 'PANDA status monitor',
                     loglevel = 'info',
                     server = 'pandasrv.panda.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     fontsize = 14,
                     valuefont = 'Luxi Mono',
                     layout = [ [_column1 ] ],
                     notifiers = [],
                     warnings = [])
)

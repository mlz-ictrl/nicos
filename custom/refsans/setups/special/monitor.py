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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=50,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='det/lastfilenumber'),
            )
        ],
        # setups='experiment'
    ),
)

# NOK's
_noklist = 'nok1 nok2 nok3 nok4 nok5a zb0 nok5b zb1 nok6 zb2 nok7 zb3 nok8 bs1 nok9'.split()
_nok_array = []
for i in range(4):
    if _noklist:
        _r = []
        for j in range(4):
            if _noklist:
                nok = _noklist.pop(0)
                _r.append(Field(dev=nok, width=16))
        _nok_array.append(BlockRow(*_r))

_nokcolumn = Column(Block('NOK-System', _nok_array))

_refcolumn = Column(
    Block('References', [
        BlockRow( Field(dev='nok_refa1', name='ref_A1'),
                  Field(dev='nok_refb1', name='ref_B1'),
                  Field(dev='nok_refc1', name='ref_C1'),),
        BlockRow( Field(dev='nok_refa2', name='ref_A2'),
                  Field(dev='nok_refb2', name='ref_B2'),
                  Field(dev='nok_refc2', name='ref_C2'),),
        ],
    ),
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'refsans10.refsans.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 5,
                     layout = [
                               Row(_expcolumn),
                               Row(_nokcolumn, _refcolumn),
                              ],
                    ),
)

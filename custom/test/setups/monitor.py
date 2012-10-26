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

description = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(name='Last file', key='filesink/lastfilenumber'))]),
)

_axisblock = Block(
    'Axes',
    [BlockRow('mth', 'mtt'),
     BlockRow('psi', 'phi'),
     BlockRow('ath', 'att'),
    ],
    'tas')  # this is the name of a setup that must be loaded in the
            # NICOS master instance for this block to be displayed

_detectorblock = Block(
    'Detector',
    [BlockRow(Field(name='timer', dev='timer'),
              Field(name='ctr1',  dev='ctr1', min=100, max=500),
              Field(name='ctr2',  dev='ctr2')),
    ],
    'detector')

_tasblock = Block(
    'Triple-axis',
    [BlockRow(Field(dev='tas', item=0, name='H', format='%.3f', unit=''),
              Field(dev='tas', item=1, name='K', format='%.3f', unit=''),
              Field(dev='tas', item=2, name='L', format='%.3f', unit=''),
              Field(dev='tas', item=3, name='E', format='%.3f', unit='')),
     BlockRow(Field(key='tas/scanmode', name='Mode'),
              Field(dev='mono', name='ki'),
              Field(dev='ana', name='kf'),
              Field(key='tas/energytransferunit', name='Unit')),
    ],
    'tas')

_tempblock = Block(
    'Temperature',
    [BlockRow(Field(dev='T'), Field(key='t/setpoint', name='Setpoint')),
     BlockRow(Field(dev='T', plot='T', interval=300, width=50),
              Field(key='t/setpoint', name='SetP', plot='T', interval=300))],
    'temperature')

_rightcolumn = Column(_axisblock, _detectorblock)

_leftcolumn = Column(_tasblock, _tempblock)


devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'localhost:14869',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 5,
                     layout = [Row(_expcolumn), Row(_rightcolumn, _leftcolumn)],
                     notifiers = [])
)

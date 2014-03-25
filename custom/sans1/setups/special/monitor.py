#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

description = 'setup for the status monitor'
group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=50,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='det/lastfilenumber'),
            )
        ],# 'experiment'
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='speed', dev='selector', width=8),
                 ),
         BlockRow(
                 Field(name='lambda', dev='selector_lambda', width=8),
                 ),
         BlockRow(
                 Field(name='position', dev='sel_ng_sw', width=8),
                 ),
         BlockRow(
                 Field(name='tilt', dev='sel_tilt', width=8),
                 ),
               ],
        ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 Field(name='Col Pump', dev='coll_p3'),
                 Field(name='Col Tube', dev='coll_p1'),
                 Field(name='Col Nose', dev='coll_p2'),
                 Field(name='Det Nose', dev='tub_p2'),
                 Field(name='Det Tube', dev='tub_p1'),
                 )],
        ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower', width=8, format = '%.2f', unit='MW'),
                 Field(name='6 Fold Shutter', dev='Sixfold', width=8),
                 Field(name='NL4a', dev='NL4a', width=8),
#                 ),
#        BlockRow(
                 Field(name='T in', dev='t_in_memograph', width=8, unit='C'),
                 Field(name='T out', dev='t_out_memograph', width=8, unit='C'),
                 Field(name='Cooling', dev='cooling_memograph', width=8, unit='kW'),
#                 ),
#        BlockRow(
                 Field(name='Flow in', dev='flow_in_memograph', width=8, unit='l/min'),
                 Field(name='Flow out', dev='flow_out_memograph', width=8, unit='l/min'),
                 Field(name='Leakage', dev='leak_memograph', width=8, unit='l/min'),
#                 ),
#        BlockRow(
                 Field(name='P in', dev='p_in_memograph', width=8, unit='bar'),
                 Field(name='P out', dev='p_out_memograph', width=8, unit='bar'),
                 Field(name='Crane Pos', dev='Crane', width=8, unit='m'),
                      ),
                ],
        ),
)

_collimationcolumn = Column(
    Block('Collimation',[
      BlockRow(
        Field(dev='at', name='att',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['x10','x100','x1000','OPEN'],
              width=6.5,height=9),
        Field(dev='ng_pol', name='pol',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','POL2','POL1','NG'],
              width=5.5,height=9),
        Field(dev='col_20a', name='20a',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_20b', name='20b',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='bg1', name='bg1',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['50mm','OPEN','20mm','42mm','N.A.'],
              width=7,height=9),
        Field(dev='col_16a', name='16a',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_16b', name='16b',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_12a', name='12a',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_12b', name='12b',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_8a', name='8a',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_8b', name='8b',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='bg2', name='bg2',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['28mm','20mm','12mm','OPEN','N.A.'],
              width=7,height=9),
        Field(dev='col_4a', name='4a',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_4b', name='4b',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_2a', name='2a',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='col_2b', name='2b',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['LAS','free','COL','NG'],
              width=5,height=9),
        Field(dev='sa1', name='sa1',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['blocked','20mm','10mm','50x50'],
              width=7,height=9),
                         ),
      BlockRow(
        Field(dev='col', name='col'),
              ),
                ],
        ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
        Field(devices=['det1_z1a', 'det1_x1a','det1_omega1a', 'det_pos2'],
                widget='nicos.sans1.monitorwidgets.Tube2', width=30, height=10)#, max=21000),
              ),
        BlockRow(
                 Field(name='det1_z', dev='det1_z1a', width=8),
                 Field(name='det1_x', dev='det1_x1a', width=8),
                 Field(name='det1_omg', dev='det1_omega1a', width=8),
                 Field(name='t', dev='det1_t_ist', width=8),
                 Field(name='t pres.', dev='det_1_t_soll', width=8),
                 Field(name='voltage', dev='hv', width=8),
                 Field(name='mon 1', dev='det1_mon1', width=8),
                 Field(name='mon 2', dev='det1_mon2', width=8),
                 Field(name='bs1_x', dev='bs1_x1a', width=8),
                 Field(name='bs1_y', dev='bs1_y1a', width=8),
                 ),
            ],
        ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'SANS-1 status monitor',
                     loglevel = 'debug',
#                     loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,#12
                     padding = 3,#3
                     layout = [
                                 Row(_expcolumn),
                                 Row(_sans1general),
                                 Row(_pressurecolumn),
                                 Row(_selcolumn,_collimationcolumn),
                                 Row(_sans1det),
                               ],
                    ),
)

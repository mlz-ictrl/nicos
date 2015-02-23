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
                 Field(name='Current status', key='exp/action', width=70,
                       istext=True, maxlen=100),
                 Field(name='Data file', key='exp/lastimage'),
                 Field(name='Current Sample', key='sample/samplename', width=16),
            )
        ],# 'experiment'
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='selector_rpm', dev='selector_rpm', width=14),
                 Field(name='selector_lambda', dev='selector_lambda', width=14),
                 ),
#         BlockRow(
#                 Field(name='selector_ng', dev='selector_ng', width=14),
#                 Field(name='selector_tilt', dev='selector_tilt', width=14, format = '%.1f'),
#                 ),
         BlockRow(
                 Field(name='water flow', dev='selector_wflow', width=14, format = '%.1f'),
                 Field(name='rotor temp.', dev='selector_rtemp', width=14, format = '%.1f'),
                 ),
               ],
        ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 Field(name='Col Pump', dev='coll_pump', width=11, format = '%g'),
                 Field(name='Col Tube', dev='coll_tube', width=11, format = '%g'),
                 Field(name='Col Nose', dev='coll_nose', width=11, format = '%g'),
                 Field(name='Det Nose', dev='det_nose', width=11, format = '%g'),
                 Field(name='Det Tube', dev='det_tube', width=11, format = '%g'),
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
        Field(dev='att', name='att',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['dia10', 'x10','x100','x1000','open'],
              width=6.5,height=9),
        Field(dev='ng_pol', name='ng_pol',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','pol2','pol1','ng'],
              width=5.5,height=9),
        Field(dev='col_20a', name='20',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_20b', name='18',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='bg1', name='bg1',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['50mm','open','20mm','42mm'],
              disabled_options = ['N.A.'],
              width=7,height=9),
        Field(dev='col_16a', name='16',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_16b', name='14',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_12a', name='12',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_12b', name='10',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_8a', name='8',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_8b', name='6',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='bg2', name='bg2',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['28mm','20mm','12mm','open'],
              disabled_options = ['N.A.'],
              width=7,height=9),
        Field(dev='col_4a', name='4',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_4b', name='3',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_2a', name='2',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='col_2b', name='1.5',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['las','free','col','ng'],
              width=5,height=9),
        Field(dev='sa1', name='sa1',
              widget='nicos.sans1.monitorwidgets.CollimatorTable',
              options=['20mm','10mm','50x50'],
              disabled_options = ['N.A.'],
              width=7,height=9),
                         ),
      BlockRow(
        Field(dev='col', name='col', unit='m', format = '%.1f'),
              ),
                ],
        ),
)

_sampleaperture = Column(
    Block('SA', [
        BlockRow(
                 Field(name='sa2', dev='sa2', width=8, format = '%g'),
                 )],
        ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
        Field(devices=['det1_z', 'det1_x','det1_omega', 'det_pos2'],
                widget='nicos.sans1.monitorwidgets.Tube2', width=30, height=10)#, max=21000),
              ),
        BlockRow(
                 Field(name='det1_z', dev='det1_z', width=12, unit='mm', format='%.0f'),
                 Field(name='det1_x', dev='det1_x', width=12, unit='mm', format='%.0f'),
                 Field(name='det1_omg', dev='det1_omg', width=12, unit='deg', format='%.0f'),
                 Field(name='t', dev='det1_t_ist', width=12),
                 Field(name='t pres.', key='det1_timer.preselection', width=12, unit='s', format='%i'),
                 Field(name='det1_hv', dev='det1_hv_ax', width=12, format='%i'),
                 Field(name='events', dev='det1_ev', width=12),
                 Field(name='mon 1', dev='det1_mon1', width=12),
                 Field(name='mon 2', dev='det1_mon2', width=12),
                 Field(name='bs1_x', dev='bs1_x', width=12, format='%.1f'),
                 Field(name='bs1_y', dev='bs1_y', width=12, format='%.1f'),
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
                     fontsize = 13,#12
                     padding = 0,#3
                     layout = [
                                 Row(_selcolumn,_collimationcolumn,_sampleaperture),
                                 Row(_sans1det),
                                 #Row(_sans1general),
                                 Row(_pressurecolumn),
                                 Row(_expcolumn),
                               ],
                    ),
)

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
                 Field(name='Sel NG', dev='sel_ng_sw'),
                 Field(name='Sel tilt', dev='sel_tilt'),
                 )
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
                 Field(name='Reactor', dev='ReactorPower', width=12, format = '%.2f', unit='MW'),
                 Field(name='6 Fold Shutter', dev='Sixfold', width=12),
                 Field(name='NL4a', dev='NL4a', width=12),
                 ),
        BlockRow(
                 Field(name='T in', dev='t_in_memograph', width=12, unit='C'),
                 Field(name='T out', dev='t_out_memograph', width=12, unit='C'),
                 Field(name='Cooling', dev='cooling_memograph', width=12, unit='kW'),
                 ),
        BlockRow(
                 Field(name='Flow in', dev='flow_in_memograph', width=12, unit='l/min'),
                 Field(name='Flow out', dev='flow_out_memograph', width=12, unit='l/min'),
                 Field(name='Leakage', dev='leak_memograph', width=12, unit='l/min'),
                 ),
        BlockRow(
                 Field(name='P in', dev='p_in_memograph', width=12, unit='bar'),
                 Field(name='P out', dev='p_out_memograph', width=12, unit='bar'),
                 Field(name='Crane Pos', dev='Crane', width=12, unit='m'),
                      ),
                ],
        ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
                 Field(name='t ist', dev='det1_t_ist', width=13),
                 Field(name='t set', dev='det_1_t_soll', width=13),),
        BlockRow(
                 Field(name='Voltage', dev='hv', width=13),
                 Field(name='det1_z-1a', dev='det1_z1a', width=13),),
        BlockRow(
                 Field(name='det1_omg-1a', dev='det1_omega1a', width=13),
                 Field(name='det1_x-1a', dev='det1_x1a', width=13),),
        BlockRow(
                 Field(name='bs1_x-1a', dev='bs1_x1a', width=13),
                 Field(name='bs1_y-1a', dev='bs1_y1a', width=13),),
                ],
        ),
)

#~ _atpolcolumn = Column(
    #~ Block('Attenuator / Polarizer',[
      #~ BlockRow(
        #~ Field(dev='at', name='Att',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ #options=['OPEN','x1000','x100','x10'],
              #~ options=['x10','x100','x1000','OPEN'],
              #~ width=7,height=7),
        #~ Field(dev='ng_pol', name='Pol',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ #options=['NG','POL1','POL2','LAS'],
              #~ options=['LAS','POL2','POL1','NG'],
              #~ width=5,height=7),),
                #~ ],
        #~ ),
#~ )

_atpolcolumn = Column(
    Block('Attenuator / Polarizer',[
      BlockRow(
               Field(dev='at', name='Att', width=7),
               Field(dev='ng_pol', name='Pol', width=7),
              ),
      ],
   ),
)


#~ _sanscolumn = Column(
    #~ Block('SANS',[
      #~ BlockRow(
#        Field(dev='at', name='Att',
#              widget='nicos.sans1.monitorwidgets.CollimatorTable',
#              #options=['OPEN','x1000','x100','x10'],
#              options=['x10','x100','x1000','OPEN'],
#              width=7,height=7),
#        Field(dev='ng_pol', name='Pol',
#              widget='nicos.sans1.monitorwidgets.CollimatorTable',
#              #options=['NG','POL1','POL2','LAS'],
#              options=['LAS','POL2','POL1','NG'],
#              width=5,height=7),
        #~ Field(dev='col_20a', name='20a',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ #options=['NG','COL','free','LAS'],
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_20b', name='20b',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_16a', name='16a',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_16b', name='16b',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_12a', name='12a',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_12b', name='12b',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_8a', name='8a',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_8b', name='8b',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_4a', name='4a',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_4b', name='4b',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_2a', name='2a',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),
        #~ Field(dev='col_2b', name='2b',
              #~ widget='nicos.sans1.monitorwidgets.CollimatorTable',
              #~ options=['LAS','free','COL','NG'],
              #~ width=5,height=7),),
#        Field(dev=['det_pos1', 'det_pos1_x','det_pos1_tilt', 'det_pos2'],
#                name='Detector position',
#                widget='nicos.sans1.monitorwidgets.Tube2', width=30, height=10, max=21),),
#     BlockRow(
#        Field(dev='col', name='Collimation length',
#              widget='nicos.sans1.monitorwidgets.BeamOption',
#              width=13, height=4),
                #~ ],
        #~ ),
#~ )

_sanscolumn = Column(
    Block('SANS',[
      BlockRow(
        Field(dev='bg1', name='bg1', width=5),
        Field(dev='bg2', name='bg2', width=5),
        Field(dev='sa1', name='sa1', width=5),
              ),
      BlockRow(
        Field(dev='col_20a', name='20a', width=5),
        Field(dev='col_16a', name='16a', width=5),
        Field(dev='col_12a', name='12a', width=5),
        Field(dev='col_8a', name='8a', width=5),
        Field(dev='col_4a', name='4a', width=5),
        Field(dev='col_2a', name='2a', width=5),
              ),
      BlockRow(
        Field(dev='col_20b', name='20b', width=5),
        Field(dev='col_16b', name='16b', width=5),
        Field(dev='col_12b', name='12b', width=5),
        Field(dev='col_8b', name='8b', width=5),
        Field(dev='col_4b', name='4b', width=5),
        Field(dev='col_2b', name='2b', width=5),
              ),
      BlockRow(
        Field(dev='col', name='col'),
              ),
    ])
)

_detvesselcolumn = Column(
    Block('Detector Vessel',[
      BlockRow(
        Field(dev=['det1_z1a', 'det1_x1a','det1_omega1a', 'det_pos2'],
                name='Detector position',
                widget='nicos.sans1.monitorwidgets.Tube2', width=30, height=10, max=21000),
              ),
         ],),
)

#~ _testblock = Block(
    #~ 'Test',
    #~ [
     #~ BlockRow(Field(gui='custom/sans1/lib/gui/test.ui')),
#~ #     BlockRow('mth', 'mtt'),
#~ #     BlockRow('psi', 'phi'),
#~ #     BlockRow('ath', 'att'),
    #~ ],
#~ )  # this is the name of a setup that must be loaded in the
            #~ # NICOS master instance for this block to be displayed

#~ _testcolumn = Column(_testblock)

#~ _fullcolumn = Column(_atpolblock, _sansblock)
#~ _sanscolumn


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'SANS-1 status monitor',
                     loglevel = 'debug',
#                     loglevel = 'info',
                     cache = 'sans1ctrl.sans1.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 3,
                     layout = [
                                 Row(_expcolumn),
                                 #Row(_testcolumn),
                                 Row(_sans1general, _sans1det),
                                 Row(_selcolumn, _pressurecolumn),
                                 Row(_atpolcolumn, _sanscolumn, _detvesselcolumn),
                               ],
                    ),
)

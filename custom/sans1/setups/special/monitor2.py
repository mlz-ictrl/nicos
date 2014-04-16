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

description = 'setup for the status monitor for SANS1'

group = 'special'


Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds


_sc1 = Block('Sample Changer 1', [
    BlockRow(Field(name='Position', dev='sc1_y'),),
    BlockRow(Field(name='sc1', dev='sc1'),),
], 'sc1'
)

_st2 = Block('Sample Table', [
    BlockRow(Field(name='st2_z', dev='st2_z'),),
    BlockRow(Field(name='st2_y', dev='st2_y'),),
    BlockRow(Field(name='st2_x', dev='st2_x'),),
], 'sample_table_2'
)

_st1 = Block('Sample Table', [
    BlockRow(Field(name='st1_phi', dev='st1_phi'),),
    BlockRow(Field(name='st1_chi', dev='st1_chi'),),
    BlockRow(Field(name='st1_omg', dev='st1_omg'),),
    BlockRow(Field(name='st1_y', dev='st1_y'),),
    BlockRow(Field(name='st1_z', dev='st1_z'),),
    BlockRow(Field(name='st1_x', dev='st1_x'),),
], 'sample_table_1'
)

_htf03 = Block('HTF03', [
    BlockRow(Field(name='Temperature', dev='T_htf03', format='%.2f', unit='C')),
    BlockRow(
             Field(name='Setpoint', key='t_htf03/setpoint',
                   format='%.1f', unit='C'),
             Field(name='Heater Power', key='t_htf03/heaterpower',
                   format='%.1f', unit='%'),
             Field(name='Vacuum', key='htf03_p'),
            ),
    BlockRow(
             Field(name='P', key='t_htf03/p', format='%i'),
             Field(name='I', key='t_htf03/i', format='%i'),
             Field(name='D', key='t_htf03/d', format='%i'),
            ),
], 'htf03')

_spinflipper = Block('Spin Flipper', [
    BlockRow(
             Field(name='Power', dev='p_sf'),
             Field(name='Frequency', dev='f_sf'),
            ),
    BlockRow(
             Field(name='Forward', dev='forward_sf'),
             Field(name='Reverse', dev='reverse_sf'),
            ),
    BlockRow(Field(name='Temperature of AG1016', dev='t_sf'),),
    BlockRow(
             Field(name='Ampl HP33220a', dev='a_agilent1'),
             Field(name='Freq HP33220a', dev='f_agilent1'),
            ),
], 'spin_flipper')

_sansmagnet = Block('Sans1 Magnet', [
    BlockRow(Field(name='Field', dev='b_overall'),),
    BlockRow(
             Field(name='Power Supply 1', dev='b_left'),
             Field(name='Power Supply 2', dev='b_right'),
            ),
    BlockRow(
             Field(name='CH Stage 1', dev='t_1'),
             Field(name='CH Stage 2', dev='t_2'),
            ),
    BlockRow(
             Field(name='Shield Top', dev='t_3'),
             Field(name='Shield Bottom', dev='t_4'),
            ),
    BlockRow(
             Field(name='Magnet TL', dev='t_5'),
             Field(name='Magnet TR', dev='t_6'),
            ),
    BlockRow(
             Field(name='Magnet BL', dev='t_8'),
             Field(name='Magnet BR', dev='t_7'),
            ),
], 'ccmsans')

_amagnet = Block('Garfield Magnet', [
    BlockRow(Field(name='Lambda out', dev='l_out'),),
    #BlockRow(Field(name='Lambda in', dev='l_in'),),
], 'amagnet')

_newport = Block('NewPort', [
    BlockRow(
             Field(name='NP 02 position', dev='sth_newport02'),
             Field(name='NP 03 position', dev='sth_newport03'),
            ),
], 'newport0*')


ccrs = []
for i in range(10, 22 + 1):
    ccrs.append(Block('CCR%d' % i, [
        BlockRow(
            Field(name='Setpoint', key='t_ccr%d_tube/setpoint' % i,
                   unitkey='t/unit'),
            Field(name='Manual Heater Power', key='t_ccr%d_tube/heaterpower' % i,
                   unitkey='t/unit'),
        ),
        BlockRow(
             Field(name='A', dev='T_ccr%d_A' % i),
             Field(name='B', dev='T_ccr%d_B' % i),
        ),
        BlockRow(
             Field(name='C', dev='T_ccr%d_C' % i),
             Field(name='D', dev='T_ccr%d_D' % i),
        ),
    ], 'ccr%d' % i))


_birmag = Block('17 T Magnet', [
        BlockRow(
                 Field(name='helium level', dev='helevel_birmag', width=13),
                 Field(name='field birmag', dev='field_birmag', width=13),),
        BlockRow(
                 Field(name='Setpoint 1 birmag', dev='sp1_birmag', width=13),
                 Field(name='Setpoint 2 birmag', dev='sp2_birmag', width=13),),
        BlockRow(
                 Field(name='Temp a birmag', dev='ta_birmag', width=13),
                 Field(name='Temp b birmag', dev='tb_birmag', width=13),),
], 'birmag')

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

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     description='Status monitor',
                     title='SANS-1 status monitor',
                     cache='sans1ctrl.sans1.frm2',
                     font='Luxi Sans',
                     fontsize=15,#12
                     loglevel='info',
                     padding=0,#3
                     prefix='nicos/',
                     valuefont='Consolas',
                     layout=[
                                Row(_sans1general),
                                Row(
                                    Column(_sc1, _st2, _st1, _amagnet, _newport),
                                    Column(_htf03, _spinflipper, _sansmagnet),
                                    Column(*ccrs) + Column(_birmag),
                                ),
                            ],
                    ),
)

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

description = 'setup for the status monitor for SANS1'

group = 'special'


Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds


_sc1 = Block('Sample Changer 1', [
    BlockRow(Field(name='Position', dev='sc1_sw'),),
    BlockRow(Field(name='sc1', dev='sc1'),),
], 'sc1')

_table = Block('Sample Table', [
    BlockRow(Field(name='z-2a', dev='z_2a'),),
    BlockRow(Field(name='y-2a', dev='y_2a'),),
    BlockRow(Field(name='x-2a', dev='x_2a'),),
    BlockRow(Field(name='phi-2b', dev='phi_2b'),),
    BlockRow(Field(name='chi-2b', dev='chi_2b'),),
    BlockRow(Field(name='omega-2b', dev='omega_2b'),),
    BlockRow(Field(name='y-2b', dev='y_2b'),),
    BlockRow(Field(name='z-2b', dev='z_2b'),),
    BlockRow(Field(name='x-2b', dev='x_2b'),),
])

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
])

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
])

_sans1magnet = Block('Sans1 Magnet', [
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
])

_newport = Block('NewPort', [
    BlockRow(
             Field(name='NP 02 position', dev='sth_newport02'),
             Field(name='NP 03 position', dev='sth_newport03'),
            ),
])

_ccr10 = Block('CCR10', [
    BlockRow(Field(name='Setpoint', key='t_ccr10_tube/setpoint',
                   unitkey='t/unit'),),
    BlockRow(
             Field(name='A', dev='T_ccr10_A'),
             Field(name='B', dev='T_ccr10_B'),
            ),
])

_ccr11 = Block('CCR11', [
    BlockRow(Field(name='Setpoint', key='t_ccr11_tube/setpoint',
                   unitkey='t/unit'),),
    BlockRow(
             Field(name='A', dev='T_ccr11_A'),
             Field(name='B', dev='T_ccr11_B'),
            ),
    BlockRow(
             Field(name='C', dev='T_ccr11_C'),
             Field(name='D', dev='T_ccr11_D'),
            ),
])

_ccr12 = Block('CCR12', [
    BlockRow(Field(name='Setpoint', key='t_ccr12_tube/setpoint',
                   unitkey='t/unit'),),
    BlockRow(
             Field(name='A', dev='T_ccr12_A'),
             Field(name='B', dev='T_ccr12_B'),
            ),
])

_ccr16 = Block('CCR16', [
    BlockRow(Field(name='Setpoint', key='t_ccr16_tube/setpoint',
                   unitkey='t/unit'),),
    BlockRow(
             Field(name='A', dev='T_ccr16_A'),
             Field(name='B', dev='T_ccr16_B'),
            ),
])

_ccr18 = Block('CCR18', [
    BlockRow(Field(name='Setpoint', key='t_ccr18_tube/setpoint',
                   unitkey='t/unit'),),
    BlockRow(
             Field(name='A', dev='T_ccr18_A'),
             Field(name='B', dev='T_ccr18_B'),
            ),
])

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     description='Status monitor',
                     title='SANS-1 status monitor',
                     cache='sans1ctrl.sans1.frm2',
                     font='Luxi Sans',
                     fontsize=12,
                     loglevel='info',
                     padding=3,
                     prefix='nicos/',
                     valuefont='Consolas',
                     layout=[
                              [
                                 [_sc1, _table],
                                 [_htf03, _spinflipper, _sans1magnet, _newport],
                                 [_ccr10, _ccr11, _ccr12, _ccr16, _ccr18],
                              ],
                            ],
                    ),
)

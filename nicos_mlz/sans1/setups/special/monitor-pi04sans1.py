#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

description = 'setup for the status monitor for SANS-1'

group = 'special'

_configuration = Column(
    Block('Configuration', [
        BlockRow(
                 Field(name='lambda', dev='selector_lambda', width=9),
                 Field(name='att', dev='att', width=9),
                 Field(name='23m', dev='ng_pol', width=9),
                 Field(name='col', dev='col', width=9, format = '%.1f'),
                 Field(name='sa1', dev='sa1', width=9),
                 Field(name='sa2', dev='sa2', width=9),
                ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
                 Field(name='det1_z', dev='det1_z', width=9, unit='mm', format='%.0f'),
                 Field(name='t', dev='det1_t_ist', width=9),
                 Field(name='t pres.', key='det1_timer.preselection', width=9, unit='s', format='%i'),
                 Field(name='det1_hv', dev='det1_hv_ax', width=9, format='%i'),
                 Field(name='events', dev='det1_ev', width=9),
                 Field(name='bs1', dev='bs1', width=9),
                ),
        ],
    ),
)

_pressure = Column(
    Block('Pressure', [
        BlockRow(
                 Field(name='Col Tube', dev='coll_tube', width=11, format = '%g'),
                 Field(name='Col Nose', dev='coll_nose', width=11, format = '%g'),
                 Field(name='Det Nose', dev='det_nose', width=11, format = '%g'),
                 Field(name='Det Tube', dev='det_tube', width=11, format = '%g'),
                ),
        ],
    ),
)

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Current status', key='exp/action', width=18,#70
                       istext=True, maxlen=90),
            )
        ],
        # setups='experiment',
    ),
)

_pressure_box = Column(
    Block('Pressure', [
        BlockRow(Field(name='Pressure', dev='pressure_box', width=9),
            )
        ],
        setups='pressure_box',
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        description = 'Status monitor',
        showwatchdog = False,
        title = 'SANS-1',
        cache = 'sans1ctrl.sans1.frm2',
        font = 'Luxi Sans',
        fontsize = 12,  # 12
        loglevel = 'info',
        padding = 0,  # 3
        prefix = 'nicos/',
        valuefont = 'Consolas',
        layout = [
            Row(_configuration, _pressure_box),
            Row(_sans1det),
            Row(_pressure, _expcolumn),
        ],
    ),
)

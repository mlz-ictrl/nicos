#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from test.utils import cache_addr

description = 'setup for the HTML status monitor'

includes = ['stdsystem']

_column1 = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=15,
                       istext=True, maxlen=15),
                 Field(name='Sample',   key='sample/samplename', width=15,
                       istext=True, maxlen=15),
                 Field(name='Remark',   key='exp/remark',   width=30,
                       istext=True, maxlen=30),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(key='exp/lastscan')),
        ],
    ),
)

_column2 = Column(
    Block('Instrument', [
        BlockRow('t_mth', 't_mtt'),
        BlockRow('t_ath', 't_att'),
        BlockRow(Field(dev='t_phi', width=4),
                 Field(dev='t_psi', width=4)),
        BlockRow(Field(dev='t_mono', width=4),
                 Field(dev='t_ana', name='Mono slit 2 (ms2)', width=20, istext=True)),
        ],
        setups='stdsystem',
    ),
    Block('Specials', [
        BlockRow(Field(picture='/some/pic.png')),
        BlockRow(Field(plot='plot', dev='t_mtt', plotwindow=3600)),
        ],
    ),
)

devices = dict(
    Monitor = device('test.test_simple.test_monitor_html.HtmlTestMonitor',
        title = 'Status monitor',
        filename = 'unused',
        interval = 10,
        cache = cache_addr,
        prefix = 'nicos/',
        layout = [[_column1, _column2]],
    ),
)

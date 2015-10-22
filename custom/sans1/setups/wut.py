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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'wut readout'

includes = []

group = 'lowlevel'

devices = dict(
    p_in_wut = device('sans1.wut.WutValue',
                            hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
                            port = '1',
                            description = 'pressure in front of filter',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'bar',
    ),
    p_out_wut = device('sans1.wut.WutValue',
                            hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
                            port = '2',
                            description = 'pressure behind of filter',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'bar',
    ),
    p_diff_wut = device('sans1.wut.WutDiff',
                            hostname = 'sans1wut-p-diff-fak40.sans1.frm2',
                            description = 'pressure in front of filter minus pressure behind filter',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'bar',
    ),
)


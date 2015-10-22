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

description = 'wut readout'

includes = []

#group = 'lowlevel'

devices = dict(
    s1_wut1 = device('sans1.wut.WutValue',
                            hostname = 'sans1wut1.office.frm2',
                            port = '1',
                            description = 'sensor 1 of wut box 1',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'mA',
    ),
    s2_wut2 = device('sans1.wut.WutValue',
                            hostname = 'sans1wut1.office.frm2',
                            port = '2',
                            description = 'sensor 2 of wut box 1',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'mA',
    ),
)


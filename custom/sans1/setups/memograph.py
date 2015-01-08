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

description = 'memograph readout'

includes = []

group = 'lowlevel'

devices = dict(
    t_in_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'T_in SANS1',
                            description = 'inlet temperature memograph',
                            fmtstr = '%.2F',
                            warnlimits = (-1, 17.5), #-1 no lower value
                            lowlevel = True,
    ),
    t_out_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'T_out SANS1',
                            description = 'outlet temperature memograph',
                            fmtstr = '%.2F',
                            lowlevel = True,
    ),
    p_in_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'P_in SANS1',
                            description = 'inlet pressure memograph',
                            fmtstr = '%.2F',
                            lowlevel = True,
    ),
    p_out_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'P_out SANS1',
                            description = 'outlet pressure memograph',
                            fmtstr = '%.2F',
                            lowlevel = True,
    ),
    flow_in_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'FLOW_in SANS1',
                            description = 'inlet flow memograph',
                            fmtstr = '%.2F',
                            lowlevel = True,
    ),
    flow_out_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'FLOW_out SANS1',
                            description = 'outlet flow memograph',
                            fmtstr = '%.2F',
                            lowlevel = True,
    ),
    leak_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'Leak SANS1',
                            description = 'leakage memograph',
                            fmtstr = '%.2F',
                            warnlimits = (-1, 1), #-1 no lower value
                            lowlevel = True,
    ),
    cooling_memograph = device('frm2.memograph.MemographValue',
                            hostname = 'memograph03.care.frm2',
                            group = 2,
                            valuename = 'Cooling SANS1',
                            description = 'cooling memograph',
                            fmtstr = '%.2F',
                            lowlevel = True,
    ),
)

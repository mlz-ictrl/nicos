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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

description = 'memograph readout for the chopper cooling system'

includes = []

group = 'lowlevel'

memograph = 'memograph07.care.frm2'
channel = 'TOF2'

devices = dict(
    t_in_ch_cooling = device('frm2.memograph.MemographValue',
                             hostname = '%s' % memograph,
                             group = 2,
                             valuename = 'T_in %s' % channel,
                             description = 'inlet temperature chopper cooling',
                             fmtstr = '%.1f',
                             warnlimits = (-1, 17.5), #-1 no lower value
                             lowlevel = False,
                             unit = 'C',
                            ),
    t_out_ch_cooling = device('frm2.memograph.MemographValue',
                              hostname = '%s' % memograph,
                              group = 2,
                              valuename = 'T_out %s' % channel,
                              description = 'outlet temperature chopper cooling',
                              fmtstr = '%.1f',
                              lowlevel = False,
                              unit = 'C',
                             ),
    p_in_ch_cooling = device('frm2.memograph.MemographValue',
                             hostname = '%s' % memograph,
                             group = 2,
                             valuename = 'P_in %s' % channel,
                             description = 'inlet pressure chopper cooling',
                             fmtstr = '%.1f',
                             lowlevel = False,
                             unit = 'bar',
                            ),
    p_out_ch_cooling = device('frm2.memograph.MemographValue',
                              hostname = '%s' % memograph,
                              group = 2,
                              valuename = 'P_out %s' % channel,
                              description = 'outlet pressure chopper cooling',
                              fmtstr = '%.1f',
                              lowlevel = False,
                              unit = 'bar',
                             ),
    flow_in_ch_cooling = device('frm2.memograph.MemographValue',
                                hostname = '%s' % memograph,
                                group = 2,
                                valuename = 'FLOW_in %s' % channel,
                                description = 'inlet flow chopper cooling',
                                fmtstr = '%.1f',
                                warnlimits = (0.2, 100), #100 no upper value
                                lowlevel = False,
                               ),
    flow_out_ch_cooling = device('frm2.memograph.MemographValue',
                                 hostname = '%s' % memograph,
                                 group = 2,
                                 valuename = 'FLOW_out %s' % channel,
                                 description = 'outlet flow chopper cooling',
                                 fmtstr = '%.1f',
                                 lowlevel = False,
                                 unit = 'l/min',
                                ),
    leak_ch_cooling = device('frm2.memograph.MemographValue',
                             hostname = '%s' % memograph,
                             group = 2,
                             valuename = 'Leak %s' % channel,
                             description = 'leakage chopper cooling',
                             fmtstr = '%.1f',
                             warnlimits = (-1, 1), #-1 no lower value
                             lowlevel = False,
                             unit = 'l/min',
                            ),
    cooling_ch_cooling = device('frm2.memograph.MemographValue',
                                hostname = '%s' % memograph,
                                group = 2,
                                valuename = 'Cooling %s' % channel,
                                description = 'cooling chopper cooling',
                                fmtstr = '%.1f',
                                lowlevel = False,
                                unit = 'kW',
                               ),
)

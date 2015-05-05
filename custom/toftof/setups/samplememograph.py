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
channel = 'TOF1'
system = 'sample'
_group = 1

devices = {
    't_in_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                            hostname = '%s' % memograph,
                                            group = _group,
                                            valuename = 'T_in %s' % channel,
                                            description = 'inlet temperature %s cooling' % system,
                                            fmtstr = '%.1f',
                                            warnlimits = (-1, 17.5), #-1 no lower value
                                            lowlevel = False,
                                            unit = 'C',
                                           ),
    't_out_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                            hostname = '%s' % memograph,
                                            group = _group,
                                            valuename = 'T_out %s' % channel,
                                            description = 'outlet temperature %s cooling' % system,
                                            fmtstr = '%.1f',
                                            lowlevel = False,
                                            unit = 'C',
                                           ),
    'p_in_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                           hostname = '%s' % memograph,
                                           group = _group,
                                           valuename = 'P_in %s' % channel,
                                           description = 'inlet pressure %s cooling' % system,
                                           fmtstr = '%.1f',
                                           lowlevel = False,
                                           unit = 'bar',
                                          ),
    'p_out_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                            hostname = '%s' % memograph,
                                            group = _group,
                                            valuename = 'P_out %s' % channel,
                                            description = 'outlet pressure %s cooling' % system,
                                            fmtstr = '%.1f',
                                            lowlevel = False,
                                            unit = 'bar',
                                           ),
    'flow_in_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                              hostname = '%s' % memograph,
                                              group = _group,
                                              valuename = 'FLOW_in %s' % channel,
                                              description = 'inlet flow %s cooling' % system,
                                              fmtstr = '%.1f',
                                              warnlimits = (0.2, 100), #100 no upper value
                                              lowlevel = False,
                                             ),
    'flow_out_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                               hostname = '%s' % memograph,
                                               group = _group,
                                               valuename = 'FLOW_out %s' % channel,
                                               description = 'outlet flow %s cooling % system',
                                               fmtstr = '%.1f',
                                               lowlevel = False,
                                               unit = 'l/min',
                                              ),
    'leak_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                           hostname = '%s' % memograph,
                                           group = _group,
                                           valuename = 'Leak %s' % channel,
                                           description = 'leakage %s cooling' % system,
                                           fmtstr = '%.1f',
                                           warnlimits = (-1, 1), #-1 no lower value
                                           lowlevel = False,
                                           unit = 'l/min',
                                          ),
    'power_%s_cooling' % system[:2]: device('frm2.memograph.MemographValue',
                                            hostname = '%s' % memograph,
                                            group = _group,
                                            valuename = 'Cooling %s' % channel,
                                            description = 'cooling %s cooling' % system,
                                            fmtstr = '%.1f',
                                            lowlevel = False,
                                            unit = 'kW',
                                           ),
}

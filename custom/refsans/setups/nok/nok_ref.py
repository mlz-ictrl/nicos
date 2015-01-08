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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************


description = 'Reference readouts for NOK Devices of REFSANS'

group = 'lowlevel'

includes = []

devices = dict(
# generated from global/inf/poti_tracing.inf
    nok_refa1  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok1, nok2r, nok2s, nok3r, nok3s',
                        tacodevice = 'test/wb_a/1_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refa2  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for b1r, b1s, nok4r, nok4s',
                        tacodevice = 'test/wb_a/2_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refb1  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok5ar, nok5as, nok5br, nok5bs, zb0',
                        tacodevice = 'test/wb_b/1_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refb2  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok6r, nok6s, zb1, zb2',
                        tacodevice = 'test/wb_b/2_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refc1  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok7r, nok7s, nok8r, zb3r, zb3s',
                        tacodevice = 'test/wb_c/1_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refc2  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for bs1r, bs1s, nok8s, nok9r, nok9s',
                        tacodevice = 'test/wb_c/2_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),
)

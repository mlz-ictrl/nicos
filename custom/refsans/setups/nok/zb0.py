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


description = "Devices for REFSANS's zb0"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# Debug (slit)
# Debug (k1)
    zb0        = device('nicos.refsans.nok_support.SingleMotorNOK',
                        description = 'ZB0',
                        motor = 'zb0_motor',
                        coder = 'zb0_motor',
                        obs = ['zb0_obs'],
                        nok_start = 4121.5,
                        nok_length = 13.0,
                        nok_end = 4134.5,
                        nok_gap = 1.0,
                        masks = dict(
                                     k1   = [-110.0, 0.0],
                                     slit = [0.0, 0.0],
                                    ),
                        nok_motor = 4128.5,
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    zb0_motor  = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of ZB0',
                        abslimits = (-180.815, 69.185),
                        userlimits = (-180.815, 69.08375),
                        bus = 'nokbus1',     # from ipcsms_*.res
                        addr = 0x37,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 10,
                        accel = 10,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 0,  # None # from ipcsms_*.res, PLEASE FIX IT!
                        zerosteps = int(703.315 * 800),  # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb0_obs    = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for ZB0',
                        reference = 'nok_refb1',
                        measure = 'zb0_poti',
                        poly = [-140.496936, 1001.42 / 1.918],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7780,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb0_poti   = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for ZB0',
                        tacodevice = '//%s/test/wb_b/1_2' % nethost,
                        scale = -1,  # mounted from top
                        lowlevel = True,
                       ),
)

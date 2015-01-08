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


description = "Devices for REFSANS's zb2"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus2']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# Debug (slit)
# Debug (k1)
    zb2        = device('nicos.refsans.nok_support.SingleMotorNOK',
                        description = 'ZB2',
                        motor = 'zb2_motor',
                        coder = 'zb2_motor',
                        obs = ['zb2_obs'],
                        nok_start = 7591.5,
                        nok_length = 6.0,
                        nok_end = 7597.5,
                        nok_gap = 1.0,
                        masks = dict(
                                     k1   = [-120.0, 0.0],
                                     slit = [0.0, 0.0],
                                    ),
                        nok_motor = 7597.5,
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    zb2_motor  = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of ZB2',
                        abslimits = (-681.9525, 568.04625),
                        userlimits = (-215.69, 93.0),
                        bus = 'nokbus2',     # from ipcsms_*.res
                        addr = 0x47,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 50,
                        accel = 50,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 68.0465,    # from ipcsms_*.res
                        zerosteps = int(681.95 * 800),   # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb2_obs    = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for ZB2',
                        reference = 'nok_refb2',
                        measure = 'zb2_poti',
                        poly = [-111.898256, 999.872 / 1.921],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7786,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb2_poti   = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for ZB2',
                        tacodevice = '//%s/test/wb_b/2_3' % nethost,
                        scale = -1,  # mounted from top
                        lowlevel = True,
                       ),
)

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


description = "Devices for REFSANS's nok5b"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus2']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok5b          = device('nicos.refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK5B',
                            nok_start = 4153.5,
                            nok_length = 1720.0,
                            nok_end = 5873.5,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok5br_axis',
                            motor_s = 'nok5bs_axis',
                            nok_motor = [4403.0, 5623.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok5br_axis    = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK5B, reactor side',
                            motor = 'nok5br_motor',
                            coder = 'nok5br_motor',
                            obs = ['nok5br_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok5br_motor   = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK5B, reactor side',
                            abslimits = (-714.85, 535.14875),
                            userlimits = (-44.85, 78.8),
                            bus = 'nokbus2',     # from ipcsms_*.res
                            addr = 0x44,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 1,
                            accel = 1,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 35.15,  # from ipcsms_*.res
                            zerosteps = int(714.85 * 800),   # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5br_obs     = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK5B, reactor side',
                            reference = 'nok_refb1',
                            measure = 'nok5br_poti',
                            poly = [-21.456294, 1002.032 / 3.848],   # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7544,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5br_poti    = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK5B, reactor side',
                            tacodevice = '//%s/test/wb_b/1_3' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok5bs_axis    = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK5B, sample side',
                            motor = 'nok5bs_motor',
                            coder = 'nok5bs_motor',
                            obs = ['nok5bs_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok5bs_motor   = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK5B, sample side',
                            abslimits = (-700.33, 549.66875),
                            userlimits = (-59.08, 93.41),
                            bus = 'nokbus2',     # from ipcsms_*.res
                            addr = 0x45,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 1,
                            accel = 1,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 49.76,  # from ipcsms_*.res
                            zerosteps = int(700.33 * 800),   # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5bs_obs     = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK5B, sample side',
                            reference = 'nok_refb1',
                            measure = 'nok5bs_poti',
                            poly = [-0.527028, 1000.991 / 3.843],    # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7536,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5bs_poti    = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK5B, sample side',
                            tacodevice = '//%s/test/wb_b/1_0' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),
)

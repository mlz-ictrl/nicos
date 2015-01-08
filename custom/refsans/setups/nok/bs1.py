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


description = "Devices for REFSANS's bs1"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus4']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# 2010-06-15 10:42:09 (slit)
# 12.01.2010 10:35:26 (k1)
    bs1        = device('nicos.refsans.nok_support.DoubleMotorNOK',
                        description = 'BS1',
                        nok_start = 9764.5,
                        nok_length = 6.0,
                        nok_end = 9770.5,
                        nok_gap = 18.0,
                        inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                        masks = dict(
                                     k1   = [-40.0, 0.0, -1.83, 0.0],
                                     slit = [0.0, 0.0, -0.67, -0.89],
                                    ),
                        motor_r = 'bs1r_axis',
                        motor_s = 'bs1s_axis',
                        nok_motor = [9764.75, 9770.25],
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    bs1r_axis  = device('nicos.devices.generic.Axis',
                        description = 'Axis of BS1, reactor side',
                        motor = 'bs1r_motor',
                        coder = 'bs1r_motor',
                        obs = ['bs1r_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    bs1r_motor = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of BS1, reactor side',
                        abslimits = (-323.075, 458.17375),
                        userlimits = (-178.0, -0.7),
                        bus = 'nokbus4',     # from ipcsms_*.res
                        addr = 0x67,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 5,
                        accel = 5,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = -41.8,  # from ipcsms_*.res
                        zerosteps = int(791.825 * 800),  # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1r_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for BS1, reactor side',
                        reference = 'nok_refc2',
                        measure = 'bs1r_poti',
                        poly = [-104.210515, 998.068 / 3.835],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7542,
                        length = 250.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1r_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for BS1, reactor side',
                        tacodevice = '//%s/test/wb_c/2_1' % nethost,
                        scale = 1,   # mounted from bottom
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    bs1s_axis  = device('nicos.devices.generic.Axis',
                        description = 'Axis of BS1, sample side',
                        motor = 'bs1s_motor',
                        coder = 'bs1s_motor',
                        obs = ['bs1s_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    bs1s_motor = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of BS1, sample side',
                        abslimits = (-177.315, 142.685),
                        userlimits = (-177.002, 139.998),
                        bus = 'nokbus4',     # from ipcsms_*.res
                        addr = 0x68,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 5,
                        accel = 5,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 89.529,     # from ipcsms_*.res
                        zerosteps = int(660.44 * 800),   # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1s_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for BS1, sample side',
                        reference = 'nok_refc2',
                        measure = 'bs1s_poti',
                        poly = [40.36065, 999.452 / 1.919],  # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7784,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1s_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for BS1, sample side',
                        tacodevice = '//%s/test/wb_c/2_2' % nethost,
                        scale = 1,   # mounted from bottom
                        lowlevel = True,
                       ),
)

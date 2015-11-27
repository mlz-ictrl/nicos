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


description = "Devices for REFSANS's nok8"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok8           = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK8',
                            nok_start = 8870.5,
                            nok_length = 880.0,
                            nok_end = 9750.5,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok8r_axis',
                            motor_s = 'nok8s_axis',
                            nok_motor = [9120.0, 9500.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok8r_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK8, reactor side',
                            motor = 'nok8r_motor',
                            coder = 'nok8r_motor',
                            obs = ['nok8r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok8r_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK8, reactor side',
                            abslimits = (-102.835, 128.415),
                            userlimits = (-102.835, 128.41),
                            bus = 'nokbus3',     # from ipcsms_*.res
                            addr = 0x54,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 80.915,     # from ipcsms_*.res
                            zerosteps = int(669.085 * 800),  # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok8r_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK8, reactor side',
                            reference = 'nok_refc1',
                            measure = 'nok8r_poti',
                            poly = [10.518174, 1001.53 / 3.85],  # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6508,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok8r_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK8, reactor side',
                            tacodevice = '//%s/test/wb_c/1_4' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok8s_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK8, sample side',
                            motor = 'nok8s_motor',
                            coder = 'nok8s_motor',
                            obs = ['nok8s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok8s_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK8, sample side',
                            abslimits = (-104.6, 131.65),
                            userlimits = (-104.6, 131.636),
                            bus = 'nokbus3',     # from ipcsms_*.res
                            addr = 0x55,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 85.499,     # from ipcsms_*.res
                            zerosteps = int(664.6 * 800),    # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok8s_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK8, sample side',
                            reference = 'nok_refc2',
                            measure = 'nok8s_poti',
                            poly = [8.752627, 998.722 / 3.85],   # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6511,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok8s_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK8, sample side',
                            tacodevice = '//%s/test/wb_c/2_0' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),
)

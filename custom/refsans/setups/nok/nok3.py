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


description = "Devices for REFSANS's nok3"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok3           = device('nicos.refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK3',
                            nok_start = 680.0,
                            nok_length = 600.0,
                            nok_end = 1280.0,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok3r_axis',
                            motor_s = 'nok3s_axis',
                            nok_motor = [831.0, 1131.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok3r_axis     = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK3, reactor side',
                            motor = 'nok3r_motor',
                            coder = 'nok3r_motor',
                            obs = ['nok3r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok3r_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK3, reactor side',
                            abslimits = (-21.967, 47.783),
                            userlimits = (-21.967, 47.782),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x34,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 20.6225,    # from ipcsms_*.res
                            zerosteps = int(229.467 * 2000),     # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3r_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK3, reactor side',
                            reference = 'nok_refa1',
                            measure = 'nok3r_poti',
                            poly = [21.830175, 997.962 / 3.846],     # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6507,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3r_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK3, reactor side',
                            tacodevice = '//%s/test/wb_a/1_3' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok3s_axis     = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK3, sample side',
                            motor = 'nok3s_motor',
                            coder = 'nok3s_motor',
                            obs = ['nok3s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok3s_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK3, sample side',
                            abslimits = (-20.9435, 40.8065),
                            userlimits = (-20.944, 40.8055),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x35,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 9.444,  # from ipcsms_*.res
                            zerosteps = int(240.694 * 2000),     # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3s_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK3, sample side',
                            reference = 'nok_refa1',
                            measure = 'nok3s_poti',
                            poly = [10.409698, 1003.196 / 3.854],    # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6506,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3s_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK3, sample side',
                            tacodevice = '//%s/test/wb_a/1_4' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),
)

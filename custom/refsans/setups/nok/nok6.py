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


description = "Devices for REFSANS's nok6"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus2', 'nokbus3']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok6           = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK6',
                            nok_start = 5887.5,
                            nok_length = 1720.0,
                            nok_end = 7607.5,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok6r_axis',
                            motor_s = 'nok6s_axis',
                            nok_motor = [6137.0, 7357.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok6r_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK6, reactor side',
                            motor = 'nok6r_motor',
                            coder = 'nok6r_motor',
                            obs = ['nok6r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok6r_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK6, reactor side',
                            abslimits = (-704.6375, 545.36125),
                            userlimits = (-68.0, 96.59125),
                            bus = 'nokbus2',     # from ipcsms_*.res
                            addr = 0x46,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 45.51,  # from ipcsms_*.res
                            zerosteps = int(704.638 * 800),  # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok6r_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK6, reactor side',
                            reference = 'nok_refb2',
                            measure = 'nok6r_poti',
                            poly = [3.823914, 997.832 / 3.846],  # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7538,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok6r_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK6, reactor side',
                            tacodevice = '//%s/test/wb_b/2_1' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok6s_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK6, sample side',
                            motor = 'nok6s_motor',
                            coder = 'nok6s_motor',
                            obs = ['nok6s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok6s_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK6, sample side',
                            abslimits = (-703.5, 546.49875),
                            userlimits = (-81.0, 110.875),
                            bus = 'nokbus3',     # from ipcsms_*.res
                            addr = 0x51,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 46.67,  # from ipcsms_*.res
                            zerosteps = int(703.5 * 800),    # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok6s_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK6, sample side',
                            reference = 'nok_refb2',
                            measure = 'nok6s_poti',
                            poly = [16.273013, 999.674 / 3.834],     # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7537,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok6s_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK6, sample side',
                            tacodevice = '//%s/test/wb_b/2_2' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),
)

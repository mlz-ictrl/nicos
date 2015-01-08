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


description = "Devices for REFSANS's nok9"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3', 'nokbus4']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok9           = device('nicos.refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK9',
                            nok_start = 9773.5,
                            nok_length = 840.0,
                            nok_end = 10613.5,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok9r_axis',
                            motor_s = 'nok9s_axis',
                            nok_motor = [10023.5, 10362.7],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok9r_axis     = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK9, reactor side',
                            motor = 'nok9r_motor',
                            coder = 'nok9r_motor',
                            obs = ['nok9r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok9r_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK9, reactor side',
                            abslimits = (-647.03375, 602.965),
                            userlimits = (-112.03425, 142.95925),
                            bus = 'nokbus3',     # from ipcsms_*.res
                            addr = 0x56,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 1,
                            accel = 1,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 103.086,    # from ipcsms_*.res
                            zerosteps = int(647.034 * 800),  # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok9r_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK9, reactor side',
                            reference = 'nok_refc2',
                            measure = 'nok9r_poti',
                            poly = [-99.195992, 1000.37 / 1.922],    # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7779,
                            length = 500.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok9r_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK9, reactor side',
                            tacodevice = '//%s/test/wb_c/2_3' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok9s_axis     = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK9, sample side',
                            motor = 'nok9s_motor',
                            coder = 'nok9s_motor',
                            obs = ['nok9s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok9s_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK9, sample side',
                            abslimits = (-663.60125, 586.3975),
                            userlimits = (-114.51425, 142.62775),
                            bus = 'nokbus4',     # from ipcsms_*.res
                            addr = 0x61,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 1,
                            accel = 1,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 86.749,     # from ipcsms_*.res
                            zerosteps = int(663.601 * 800),  # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok9s_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK9, sample side',
                            reference = 'nok_refc2',
                            measure = 'nok9s_poti',
                            poly = [80.372504, 998.695 / 1.919],     # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7789,
                            length = 500.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok9s_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK9, sample side',
                            tacodevice = '//%s/test/wb_c/2_4' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),
)

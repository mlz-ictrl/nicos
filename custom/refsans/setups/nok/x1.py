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


description = "Devices for REFSANS's x1"

group = 'lowlevel'

includes = ['nokbus4']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# 08.06.2009 15:29:16 (k1)
# 07.06.2009 12:56:01 (k2)
# 08.06.2009 15:29:57 (k3)
# 08.06.2009 15:29:58 (k4)
# ungenau 11.01.2010 15:01:38 (k5)
# 15/05/2012 15:19:20 JFM scann matthias the zero is at -0.1 for b1 should not you then have 6.0 (slit)
# just to test mask 2.0 (f6)
    x1         = device('refsans.nok_support.DoubleMotorNOK',
                        description = 'X1',
                        inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                        masks = dict(
                                     f6   = [0.0, -119.0, 0.0, 0.0],
                                     k1   = [-119.0, 0.0, -3.75, 0.0],
                                     k2   = [-60.0, 0.0, -2.59, 0.0],
                                     k3   = [60.0, 0.0, -2.64, 0.0],
                                     k4   = [120.0, 0.0, -2.8, 0.0],
                                     k5   = [180.0, 1.0, 0.0, 0.0],
                                     slit = [0.0, 0.0, -6.0, -2.8],
                                    ),
                        motor_r = 'x1r_axis',
                        motor_s = 'x1s_axis',
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    x1r_axis   = device('devices.generic.Axis',
                        description = 'Axis of X1, reactor side',
                        motor = 'x1r_motor',
                        coder = 'x1r_motor',
                        obs = ['x1r_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    x1r_motor  = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of X1, reactor side',
                        abslimits = (-162.899, 337.1005),
                        userlimits = (-130.0, 170.0),
                        bus = 'nokbus4',     # from addr
                        addr = 0x63,     # from resources.inf
                        slope = 2000.0,  # FULL steps per physical unit
                        speed = 200,
                        accel = 200,
                        confbyte = 32,
                        ramptype = 1,    # unknown value, PLEASE FIX IT!
                        microstep = 1,
                        refpos = 0,  # unknown
                        zerosteps = int(162.899 * 2000),     # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    x1s_axis   = device('devices.generic.Axis',
                        description = 'Axis of X1, sample side',
                        motor = 'x1s_motor',
                        coder = 'x1s_motor',
                        obs = ['x1s_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    x1s_motor  = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of X1, sample side',
                        abslimits = (-413.767, 86.2325),
                        userlimits = (-178.0, 75.0),
                        bus = 'nokbus4',     # from addr
                        addr = 0x64,     # from resources.inf
                        slope = 2000.0,  # FULL steps per physical unit
                        speed = 200,
                        accel = 200,
                        confbyte = 32,
                        ramptype = 1,    # unknown value, PLEASE FIX IT!
                        microstep = 1,
                        refpos = 0,  # unknown
                        zerosteps = int(413.767 * 2000),     # offset * slope
                        lowlevel = True,
                       ),
)

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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'Spin Flipper'

includes = []

group = 'optional'

modules = ['sans1.spinflipper_commands']

tango_host = 'spinflip.sans1.frm2'

devices = dict(
# AG1016 amplifier
    P_spinflipper = device('sans1.spinflipper.SpinflipperPower',
                           description = 'overall power of ag1016',
                           tangodevice = 'tango://%s:10000/box/amplifier/power' % tango_host,
                           forwardtangodevice = 'tango://%s:10000/box/amplifier/fpower' % tango_host,
                           reversetangodevice = 'tango://%s:10000/box/amplifier/rpower' % tango_host,
                           fmtstr = '%.1f',
                           abslimits = (0.0, 100.0),
                           userlimits = (0.0, 100.0),
                           maxage = 120,
                           pollinterval = 15,
                          ),

    P_spinflipper_forward = device('devices.generic.ReadonlyParamDevice',
                                   description = 'Paramdevice used to select the forward power',
                                   lowlevel = True,
                                   device = 'P_spinflipper',
                                   parameter = 'forward',
                                   maxage = 120,
                                   pollinterval = 15,
                                  ),

    P_spinflipper_reverse = device('devices.generic.ReadonlyParamDevice',
                                   description = 'Paramdevice used to select the reverse power',
                                   lowlevel = True,
                                   device = 'P_spinflipper',
                                   parameter = 'reverse',
                                   maxage = 120,
                                   pollinterval = 15,
                                  ),

    T_spinflipper = device('devices.tango.AnalogInput',
                           description = 'temperature of ag1016',
                           tangodevice = 'tango://%s:10000/box/amplifier/temp' % tango_host,
                           fmtstr = '%.3f',
                           maxage = 120,
                           pollinterval = 15,
                          ),

# HP33220A
    A_spinflipper_hp = device('devices.tango.AnalogOutput',
                              description = 'amplitude of the frequency generator',
                              tangodevice = 'tango://%s:10000/box/funcgen/ampl' % tango_host,
                              fmtstr = '%.3f',
                              abslimits = (0, 2.0),
                              userlimits = (0, 2.0),
                              maxage = 120,
                              pollinterval = 15,
                             ),

    F_spinflipper_hp = device('devices.tango.AnalogOutput',
                              description = 'frequency of the frequency generator',
                              tangodevice = 'tango://%s:10000/box/funcgen/freq' % tango_host,
                              fmtstr = '%.0f',
                              abslimits = (0.0, 4000000.0),
                              userlimits = (0.0, 4000000.0),
                              maxage = 120,
                              pollinterval = 15,
                             ),
)

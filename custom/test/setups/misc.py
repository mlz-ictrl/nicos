#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

description = 'miscellaneous devices'
group = 'basic'

includes = ['system']
excludes = ['excluded']

devices = dict(
    m1       = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      #loglevel = 'debug',
                      abslimits = (-100, 100),
                      speed = 0.5,
                      unit = 'deg'),

    m2       = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      loglevel = 'debug',
                      abslimits = (-100, 100),
                      speed = 1,
                      unit = 'deg'),

    c1       = device('devices.generic.VirtualCoder',
                      lowlevel = True,
                      motor = 'm1',
                      unit = 'deg'),

    a1       = device('devices.generic.Axis',
                      motor = 'm1',
                      coder = 'c1',
                      obs = ['c1'],
                      abslimits = (0, 100),
                      userlimits = (0, 50),
                      precision = 0,
                      pollinterval = 0.5),

    a2       = device('devices.generic.Axis',
                      motor = 'm2',
                      coder = 'm2',
                      obs = [],
                      precision = 0,
                      abslimits = (0, 100)),

    sw       = device('devices.generic.Switcher',
                      moveable = 'a2',
                      states = ['in', 'out'],
                      values = [1, 0],
                      precision = 0),

    ap       = device('devices.generic.DeviceAlias',
                      alias = 'a1',
                      devclass = 'nicos.core.Moveable'),

    a1speed  = device('devices.generic.ParamDevice',
                      device = 'a1',
                      parameter = 'speed'),

    sxl      = device('devices.generic.VirtualMotor',
                      abslimits = (-20, 40),
                      unit = 'mm'),
    sxr      = device('devices.generic.VirtualMotor',
                      abslimits = (-40, 20),
                      unit = 'mm'),
    sxb      = device('devices.generic.VirtualMotor',
                      abslimits = (-50, 30),
                      unit = 'mm'),
    sxt      = device('devices.generic.VirtualMotor',
                      abslimits = (-30, 50),
                      unit = 'mm'),
    slit     = device('devices.generic.Slit',
                      left = 'sxl',
                      right = 'sxr',
                      bottom = 'sxb',
                      top = 'sxt'),

    mm       = device('devices.generic.ManualMove',
                      abslimits = (0, 100),
                      unit = 'mm'),
    msw      = device('devices.generic.ManualSwitch',
                      states = ['unknown', 'on', 'off']),
)

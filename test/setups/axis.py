#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

name = 'test_axis setup'

includes = ['stdsystem']

devices = dict(
    motor = device('nicos.devices.generic.VirtualMotor',
                   unit = 'mm',
                   initval = 0,
                   abslimits = (-100, 100),
                  ),

    coder = device('nicos.devices.generic.VirtualCoder',
                   motor = 'motor',
                   unit = 'mm',
                   lowlevel = True,
                  ),

    axis = device('nicos.devices.generic.Axis',
                  motor = 'motor',
                  coder = 'coder',
                  obs = [],
                  precision = 0,
                  userlimits = (-50, 50),
                  loopdelay = 0.02,
                  loglevel = 'debug',
                 ),

    limit_axis = device('nicos.devices.generic.Axis',
                        motor = 'motor',
                        coder = 'coder',
                        obs = [],
                        abslimits = (-1, 1),
                        precision = 0,
                       ),

    backlash_axis = device('nicos.devices.generic.Axis',
                           motor = 'motor',
                           coder = 'coder',
                           obs = None,
                           backlash = 0.5,
                           precision = 0,
                           userlimits = (-50, 50),
                           loopdelay = 0.02,
                          ),

    coder2 = device('nicos.devices.generic.VirtualCoder',
                    motor = 'motor',
                    unit = 'mm',
                   ),

    obs_axis = device('nicos.devices.generic.Axis',
                      motor = 'motor',
                      coder = 'coder',
                      obs = ['coder2'],
                      backlash = 0.5,
                      precision = 0,
                      userlimits = (-50, 50),
                      loopdelay = 0.02,
                     ),
)

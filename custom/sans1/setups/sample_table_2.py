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

description = 'top sample table devices'

includes = ['sample_table_1']

group = 'optional'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    st2_z    = device('devices.generic.Axis',
                      description = 'table 2 z axis',
                      pollinterval = 15,
                      maxage = 60,
                      fmtstr = '%.2f',
                      abslimits = (-10, 10),
                      precision = 0.01,
                      motor = 'st2_zmot',
                      coder = 'st2_zenc',
                      obs=[],
                     ),
    st2_zmot = device('devices.taco.motor.Motor',
                      description = 'sample table 2 z motor',
                      tacodevice = '//%s/sans1/table/z-2amot' % (nethost, ),
                      fmtstr = '%.2f',
                      abslimits = (-10, 10),
                      lowlevel = True,
                     ),
    st2_zenc = device('devices.taco.coder.Coder',
                      description = 'sample table 2 z encoder',
                      tacodevice = '//%s/sans1/table/z-2aenc' % (nethost, ),
                      fmtstr = '%.2f',
                      lowlevel = True,
                     ),

    st2_y    = device('devices.generic.Axis',
                      description = 'table 2 y axis',
                      pollinterval = 15,
                      maxage = 60,
                      fmtstr = '%.2f',
                      abslimits = (-10, 10),
                      precision = 0.01,
                      motor = 'st2_ymot',
                      coder = 'st2_yenc',
                      obs=[],
                     ),
    st2_ymot = device('devices.taco.motor.Motor',
                      description = 'sample table 2 y motor',
                      tacodevice = '//%s/sans1/table/y-2amot' % (nethost, ),
                      fmtstr = '%.2f',
                      abslimits = (-10, 10),
                      lowlevel = True,
                     ),
    st2_yenc = device('devices.taco.coder.Coder',
                      description = 'sample table 2 y ',
                      tacodevice = '//%s/sans1/table/y-2aenc' % (nethost, ),
                      fmtstr = '%.2f',
                      lowlevel = True,
                     ),

    st2_x    = device('devices.generic.Axis',
                      description = 'table 2 x axis',
                      pollinterval = 15,
                      maxage = 60,
                      fmtstr = '%.2f',
                      abslimits = (-25, 25),
                      precision = 0.01,
                      motor = 'st2_xmot',
                      coder = 'st2_xenc',
                      obs=[],
                     ),
    st2_xmot = device('devices.taco.motor.Motor',
                      description = 'sample table 2 x motor',
                      tacodevice = '//%s/sans1/table/x-2amot' % (nethost, ),
                      fmtstr = '%.2f',
                      abslimits = (-25, 25),
                      lowlevel = True,
                     ),
    st2_xenc = device('devices.taco.coder.Coder',
                      description = 'sample table 2 x encoder',
                      tacodevice = '//%s/sans1/table/x-2aenc' % (nethost, ),
                      fmtstr = '%.2f',
                      lowlevel = True,
                     ),
)

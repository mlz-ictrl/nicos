#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

includes = ['system']

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    z_2a    = device('devices.taco.axis.Axis',
                     description = 'table z-2a axis',
                     tacodevice = '//%s/sans1/table/z-2a' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-10, 10),
                    ),
    z_2amot = device('devices.taco.motor.Motor',
                     description = 'table z-2a motor',
                     tacodevice = '//%s/sans1/table/z-2amot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-10, 10),
                    ),
    z_2aenc = device('devices.taco.coder.Coder',
                     description = 'table z-2a encoder',
                     tacodevice = '//%s/sans1/table/z-2aenc' % (nethost, ),
                     fmtstr = '%.2f',
                    ),

    y_2a    = device('devices.taco.axis.Axis',
                     description = 'table y-2a axis',
                     tacodevice = '//%s/sans1/table/y-2a' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-10, 10),
                    ),
    y_2amot = device('devices.taco.motor.Motor',
                     description = 'table y-2a motor',
                     tacodevice = '//%s/sans1/table/y-2amot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-10, 10),
                    ),
    y_2aenc = device('devices.taco.coder.Coder',
                     description = 'table y-2a encoder',
                     tacodevice = '//%s/sans1/table/y-2aenc' % (nethost, ),
                     fmtstr = '%.2f',
                    ),

    x_2a    = device('devices.taco.axis.Axis',
                     description = 'table x-2a axis',
                     tacodevice = '//%s/sans1/table/x-2a' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-25, 25),
                    ),
    x_2amot = device('devices.taco.motor.Motor',
                     description = 'table x-2a motor',
                     tacodevice = '//%s/sans1/table/x-2amot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-25, 25),
                    ),
    x_2aenc = device('devices.taco.coder.Coder',
                     description = 'table x-2a encoder',
                     tacodevice = '//%s/sans1/table/x-2aenc' % (nethost, ),
                     fmtstr = '%.2f',
                    ),
)

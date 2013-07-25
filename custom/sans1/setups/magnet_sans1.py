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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'Sans1 Magnet'

includes = ['system']

# group = 'optional'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    b_left = device('devices.taco.CurrentSupply',
                     description = 'The left? magnetic field',
                     tacodevice = '//%s/sans1/ips/1' % (nethost,),
                     abslimits = (-1, 160),
                     fmtstr = '%.3f',
                     maxage = 120,
                     pollinterval = 15,
                    ),
    b_right = device('devices.taco.CurrentSupply',
                     description = 'The right? magnetic field',
                     tacodevice = '//%s/sans1/ips/2' % (nethost,),
                     abslimits = (-1, 160),
                     fmtstr = '%.3f',
                     maxage = 120,
                     pollinterval = 15,
                    ),
    b_overall = device('devices.taco.CurrentSupply',
                     description = 'The resulting magnetic field',
                     tacodevice = '//%s/sans1/oxford/magnet' % (nethost, ),
                     abslimits = (-5, 5),
                     fmtstr = '%.3f',
                     maxage = 120,
                     pollinterval = 15,
                    ),
)

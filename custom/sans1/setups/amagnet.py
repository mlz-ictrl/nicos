#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

description = 'Garfield Magnet'

includes = ['system']

# group = 'optional'

nethost = 'amagnet.sans1.frm2'

devices = dict(
    l_in = device('devices.taco.CurrentSupply',
                     description = 'Current from power supply into the magnet',
                     tacodevice = '//%s/amagnet/lambda/in' % (nethost,),
                     abslimits = (-1, 160),
                     fmtstr = '%.3f',
                     maxage = 120,
                     pollinterval = 15,
                    ),
    l_out = device('devices.taco.CurrentSupply',
                     description = 'Current from magnet to power supply',
                     tacodevice = '//%s/amagnet/lambda/out' % (nethost,),
                     abslimits = (-1, 160),
                     fmtstr = '%.3f',
                     maxage = 120,
                     pollinterval = 15,
                    ),

)

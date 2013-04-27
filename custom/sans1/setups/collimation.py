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
#
# *****************************************************************************

description = 'Vacuum sensors of collimation tube'

includes = ['system']

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    p_c_tube = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/coll/p1' % (nethost, ),
                     fmtstr = '%.3f',
                     pollinterval = 15,
                     maxage = 60,
                   ),
    p_c_nose = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/coll/p2' % (nethost, ),
                     fmtstr = '%.3f',
                     pollinterval = 15,
                     maxage = 60,
                   ),
    p_c_pump = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/coll/p3' % (nethost, ),
                     fmtstr = '%.3f',
                     pollinterval = 15,
                     maxage = 60,
                   ),
)

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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

description = 'Selector'

includes = ['system']

group = 'basic'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
#    sel_speed    = device('devices.taco.axis.Axis',
#                     tacodevice = '//%s/sans1/table/z-2a' % (nethost, ),
#                     fmtstr = '%.2f',
#                     abslimits = (-10, 10),
#                    ),
    sel_ng    = device('devices.generic.Axis',
                       motor = 'sel_ng_mot',
                       coder = 'sel_ng_enc',
                       obs = [],
                       precision = 0.1,
                       fmtstr = '%.2f',
                       abslimits = (-140, 140),
                       maxage = 120,
                       pollinterval = 15,
                      ),
    sel_ng_mot = device('devices.taco.motor.Motor',
                        tacodevice = '//%s/sel/z/motor' % (nethost, ),
                        fmtstr = '%.2f',
                        abslimits = (-140, 140),
                        ),
    sel_ng_enc = device('devices.taco.coder.Coder',
                        tacodevice = '//%s/sel/z/enc' % (nethost, ),
                        fmtstr = '%.2f',
                       ),

    sel_ng_sw    = device('devices.generic.Switcher',
                          lowlevel = True,
                          moveable = 'sel_ng',
                          mapping = {'sel1': -140, 'ng': 0, 'sel2': 140},
                          precision = 0.01,
                         ),

    sel_tilt    = device('devices.generic.Axis',
                         motor = 'sel_tilt_mot',
                         coder = 'sel_tilt_enc',
                         obs = [],
                         precision = 0.1,
                         fmtstr = '%.2f',
                         abslimits = (-20, 20),
                         maxage = 120,
                         pollinterval = 15,
                         offset = 1,
                        ),
    sel_tilt_mot = device('devices.taco.motor.Motor',
                          tacodevice = '//%s/sel/tilt/motor' % (nethost, ),
                          fmtstr = '%.2f',
                          abslimits = (-20, 20),
                         ),
    sel_tilt_enc = device('devices.taco.coder.Coder',
                          tacodevice = '//%s/sel/tilt/enc' % (nethost, ),
                          fmtstr = '%.2f',
                         ),

)

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
# *****************************************************************************

description = 'Selector Tower Movement'

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
#    selector_speed    = device('devices.taco.axis.Axis',
#                               tacodevice = '//%s/sans1/table/z-2a' % (nethost, ),
#                               fmtstr = '%.2f',
#                               abslimits = (-10, 10),
#                              ),
    selector_ng_ax    = device('devices.generic.Axis',
                               description = 'selector neutron guide axis',
                               motor = 'selector_ng_mot',
                               coder = 'selector_ng_enc',
                               obs = [],
                               precision = 0.1,
                               fmtstr = '%.2f',
                               #abslimits = (-140, 140), alt
                               abslimits = (-140, 142), #new
                               userlimits = (-140, 142), #new
                               maxage = 120,
                               pollinterval = 15,
                               lowlevel = True,
                              ),
    selector_ng_mot = device('devices.taco.motor.Motor',
                             description = 'selector neutron guide motor',
                             tacodevice = '//%s/sel/z/motor' % (nethost, ),
                             fmtstr = '%.2f',
                             #abslimits = (-140, 140), old
                             abslimits = (-140, 142), #new
                             userlimits = (-140, 142), #new
                             lowlevel = True,
                            ),
    selector_ng_enc = device('devices.taco.coder.Coder',
                             description = 'selector neutron guide encoder',
                             tacodevice = '//%s/sel/z/enc' % (nethost, ),
                             fmtstr = '%.2f',
                             lowlevel = True,
                            ),

    selector_ng    = device('devices.generic.Switcher',
                            description = 'selector neutron guide switcher',
                            #lowlevel = True,
                            moveable = 'selector_ng_ax',
                            #mapping = {'sel1': -140, 'ng': 0, 'sel2': 140}, old value
                            mapping = {'SEL1': -138.4, 'NG': 1.6, 'SEL2': 141.6}, #new "tisane"-value
                            precision = 0.01,
                           ),

    selector_tilt    = device('devices.generic.Axis',
                              description = 'selector tilt axis',
                              motor = 'selector_tilt_mot',
                              coder = 'selector_tilt_enc',
                              obs = [],
                              precision = 0.05,
                              fmtstr = '%.1f',
                              abslimits = (-10, 10),
                              maxage = 120,
                              pollinterval = 15,
                              #offset = 1, old
                              offset = 1.72, #new
                             ),
    selector_tilt_mot = device('devices.taco.motor.Motor',
                               description = 'selector tilt motor',
                               tacodevice = '//%s/sel/tilt/motor' % (nethost, ),
                               fmtstr = '%.2f',
                               abslimits = (-10, 10),
                               lowlevel = True,
                              ),
    selector_tilt_enc = device('devices.taco.coder.Coder',
                               description = 'selector tilt encoder',
                               tacodevice = '//%s/sel/tilt/enc' % (nethost, ),
                               fmtstr = '%.2f',
                               lowlevel = True,
                              ),

)

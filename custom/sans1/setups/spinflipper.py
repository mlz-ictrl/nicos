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

description = 'Spin Flipper'

includes = []

group = 'optional'

nethost = 'spinflip02.sans1.frm2'

devices = dict(
    P_spinflipper = device('devices.taco.AnalogInput',
                           description = 'overall power of ag1016',
                           tacodevice = '//%s/spinflip/ag1016/power' % (nethost,),
                           fmtstr = '%.1f',
                          ),

    F_spinflipper = device('devices.taco.AnalogInput',
                           description = 'frequency of ag1016',
                           tacodevice = '//%s/spinflip/ag1016/frequency' % (nethost,),
                           fmtstr = '%.1f',
                          ),

    P_spinflipper_forward = device('devices.taco.AnalogInput',
                                   description = 'forward power of ag1016',
                                   tacodevice = '//%s/spinflip/ag1016/forward' % (nethost,),
                                   fmtstr = '%.1f',
                                  ),

    P_spinflipper_reverse = device('devices.taco.AnalogInput',
                                   description = 'reverse power of ag1016',
                                   tacodevice = '//%s/spinflip/ag1016/reverse' % (nethost,),
                                   fmtstr = '%.1f',
                                  ),

    T_spinflipper_ag1016 = device('devices.taco.AnalogInput',
                                  description = 'temperature of ag1016',
                                  tacodevice = '//%s/spinflip/ag1016/temperature' % (nethost,),
                                  fmtstr = '%.3f',
                                 ),

    A_spinflipper_agilent = device('devices.taco.AnalogInput',
                                   description = 'amplitude of the frequency generator',
                                   tacodevice = '//%s/spinflip/agilent/amp' % (nethost,),
                                   fmtstr = '%.3f',
                                  ),

    F_spinflipper_agilent = device('devices.taco.AnalogInput',
                                   description = 'frequency of the frequency generator',
                                   tacodevice = '//%s/spinflip/agilent/freq' % (nethost,),
                                   fmtstr = '%.0f',
                                  ),

)


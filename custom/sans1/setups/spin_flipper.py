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

includes = ['system']

group = 'optional'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    p_sf = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/ag1016/power' % (nethost,),
                        fmtstr = '%.1f',
                    ),

    f_sf = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/ag1016/frequency' % (nethost,),
                        fmtstr = '%.1f',
                    ),

    forward_sf = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/ag1016/forward' % (nethost,),
                        fmtstr = '%.1f',
                    ),

    reverse_sf = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/ag1016/reverse' % (nethost,),
                        fmtstr = '%.1f',
                    ),

    t_sf = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/ag1016/temperature' % (nethost,),
                        fmtstr = '%.3f',
                    ),
    a_agilent1 = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/agilent1/amp' % (nethost,),
                        fmtstr = '%.3f',
                    ),
    f_agilent1 = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/agilent1/freq' % (nethost,),
                        fmtstr = '%.0f',
                    ),

)


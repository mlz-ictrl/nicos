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

description = 'Birmingham Magnet 17T'

group = 'optional'

includes = ['alias_B']

nethost = 'spinflip.sans1.frm2'

devices = dict(
    B_birmag = device('devices.taco.AnalogInput',
                      description = 'magnetic field of birmingham magnet',
                      tacodevice = '//%s/spinflip/birmag/field' % (nethost,),
                      fmtstr = '%.3f',
                     ),

    T_birmag_a = device('devices.taco.AnalogInput',
                        description = 'temperature a of birmingham magnet',
                        tacodevice = '//%s/spinflip/birmag/sensa' % (nethost,),
                        fmtstr = '%.3f',
                       ),

    T_birmag_b = device('devices.taco.AnalogInput',
                        description = 'temperature b of birmingham magnet',
                        tacodevice = '//%s/spinflip/birmag/sensb' % (nethost,),
                        fmtstr = '%.3f',
                       ),

    birmag_sp1 = device('devices.taco.AnalogInput',
                        description = 'setpoint 1 of birmingham magnet',
                        tacodevice = '//%s/spinflip/birmag/sp1' % (nethost,),
                        fmtstr = '%.3f',
                       ),

    birmag_sp2 = device('devices.taco.AnalogInput',
                        description = 'setpoint 2 of birmingham magnet',
                        tacodevice = '//%s/spinflip/birmag/sp2' % (nethost,),
                        fmtstr = '%.3f',
                       ),

    birmag_helevel = device('devices.taco.AnalogInput',
                            description = 'helium level of birmingham magnet',
                            tacodevice = '//%s/spinflip/birmag/helevel' % (nethost,),
                            fmtstr = '%.3f',
                           ),

)
alias_config = [
    ('B', 'B_birmag', 100),
]

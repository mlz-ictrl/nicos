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

description = 'top sample table devices'

includes = ['system']

# included by sans1
group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    omega_2b    = device('devices.taco.axis.Axis',
                         description = 'table omega-2b axis',
                         tacodevice = '//%s/sans1/table/omega-2b' % (nethost, ),
                         pollinterval = 15,
                         maxage = 60,
                         fmtstr = '%.2f',
                         abslimits = (-180, 180),
                        ),
    omega_2bmot = device('devices.taco.motor.Motor',
                         description = 'table omega-2b motor',
                         tacodevice = '//%s/sans1/table/omega-2bmot' % (nethost, ),
                         fmtstr = '%.2f',
                         abslimits = (-180, 180),
                        ),
    omega_2benc = device('devices.taco.coder.Coder',
                         description = 'table omega-2b encoder',
                         tacodevice = '//%s/sans1/table/omega-2benc' % (nethost, ),
                         fmtstr = '%.2f',
                        ),

    chi_2b    = device('devices.taco.axis.Axis',
                       description = 'table chi-2b axis',
                       tacodevice = '//%s/sans1/table/chi-2b' % (nethost, ),
                       pollinterval = 15,
                       maxage = 60,
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                      ),
    chi_2bmot = device('devices.taco.motor.Motor',
                       description = 'table chi-2b motor',
                       tacodevice = '//%s/sans1/table/chi-2bmot' % (nethost, ),
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                       lowlevel = True,
                      ),
    chi_2benc = device('devices.taco.coder.Coder',
                       description = 'table chi-2b encoder',
                       tacodevice = '//%s/sans1/table/chi-2benc' % (nethost, ),
                       fmtstr = '%.2f',
                       lowlevel = True,
                      ),

    phi_2b    = device('devices.taco.axis.Axis',
                       description = 'table phi-2b axis',
                       tacodevice = '//%s/sans1/table/phi-2b' % (nethost, ),
                       pollinterval = 15,
                       maxage = 60,
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                      ),
    phi_2bmot = device('devices.taco.motor.Motor',
                       description = 'table phi-2b motor',
                       tacodevice = '//%s/sans1/table/phi-2bmot' % (nethost, ),
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                       lowlevel = True,
                      ),
    phi_2benc = device('devices.taco.coder.Coder',
                       description = 'table phi-2b encoder',
                       tacodevice = '//%s/sans1/table/phi-2benc' % (nethost, ),
                       fmtstr = '%.2f',
                       lowlevel = True,
                      ),

    y_2b    = device('devices.taco.axis.Axis',
                     description = 'table y-2b axis',
                     tacodevice = '//%s/sans1/table/y-2b' % (nethost, ),
                     pollinterval = 15,
                     maxage = 60,
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                    ),
    y_2bmot = device('devices.taco.motor.Motor',
                     description = 'table y-2b motor',
                     tacodevice = '//%s/sans1/table/y-2bmot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                     lowlevel = True,
                    ),
    y_2benc = device('devices.taco.coder.Coder',
                     description = 'table y-2b encoder',
                     tacodevice = '//%s/sans1/table/y-2benc' % (nethost, ),
                     fmtstr = '%.2f',
                     lowlevel = True,
                    ),

    z_2b    = device('devices.taco.axis.Axis',
                     description = 'table z-2b axis',
                     tacodevice = '//%s/sans1/table/z-2b' % (nethost, ),
                     pollinterval = 15,
                     maxage = 60,
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                    ),
    z_2bmot = device('devices.taco.motor.Motor',
                     description = 'table z-2b motor',
                     tacodevice = '//%s/sans1/table/z-2bmot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                     lowlevel = True,
                    ),
    z_2benc = device('devices.taco.coder.Coder',
                     description = 'table z-2b encoder',
                     tacodevice = '//%s/sans1/table/z-2benc' % (nethost, ),
                     fmtstr = '%.2f',
                     lowlevel = True,
                    ),

    x_2b    = device('devices.taco.axis.Axis',
                     description = 'table x-2b axis',
                     tacodevice = '//%s/sans1/table/x-2b' % (nethost, ),
                     pollinterval = 15,
                     maxage = 60,
                     fmtstr = '%.2f',
                     abslimits = (-750, 150),
                    ),
    x_2bmot = device('devices.taco.motor.Motor',
                     description = 'table x-2b motor',
                     tacodevice = '//%s/sans1/table/x-2bmot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-750, 150),
                     lowlevel = True,
                    ),
    x_2benc = device('devices.taco.coder.Coder',
                     description = 'table x-2b encoder',
                     tacodevice = '//%s/sans1/table/x-2benc' % (nethost, ),
                     fmtstr = '%.2f',
                     lowlevel = True,
                    ),
)

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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

description = 'sample table devices'

# includes = ['system']

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    sample_motor  = device('devices.taco.motor.Motor',
                           tacodevice = '//%s/pgaa/phytronixe/sample' % (nethost,),
                           fmtstr = '%7.3f',
                           abslimits = (-5, 356),
                          ),
    sample = device('devices.generic.Switcher',
                    moveable = 'sample_motor',
                    mapping  = {'1' : 4.00,
                                '2' : 74.00,
                                '3' : 144.00,
                                '4' : 214.00,
                                '5' : 284.00,
                                '6' : 354.00,
                               },
                    precision = 0.1,
                    blockingmove = False,
                    unit = '',
                   ),
    e1    = device('devices.taco.Coder',
                   tacodevice = '//%s/pgaa/phytronixe/e1' % (nethost,),
                   fmtstr = '%7.3f',
                  ),
    ellip = device('devices.taco.DigitalInput',
                   tacodevice = '//%s/pgaa/phytronixe/ellip' % (nethost,),
                  ),
    ftube = device('devices.taco.DigitalInput',
                   tacodevice = '//%s/pgaa/phytronixe/ftube' % (nethost,),
                  ),
    press1 = device('devices.taco.DigitalInput',
                    tacodevice = '//%s/pgaa/phytronixe/press1' % (nethost,),
                   ),
    press2 = device('devices.taco.DigitalInput',
                    tacodevice = '//%s/pgaa/phytronixe/press2' % (nethost,),
                   ),
)

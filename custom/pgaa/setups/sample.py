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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

description = 'sample table devices'

# includes = ['system']

nethost= '//pgaasrv.pgaa.frm2/'

devices = dict(
    e1    = device('devices.taco.Coder',
                   tacodevice = nethost + 'pgaa/phytronixe/e1',
                   fmtstr = '%7.3f',
                  ),
    ellip = device('devices.taco.DigitalInput',
                   tacodevice = nethost + 'pgaa/phytronixe/ellip',
                  ),
    ftube = device('devices.taco.DigitalInput',
                   tacodevice = nethost + 'pgaa/phytronixe/ftube',
                  ),
    press1 = device('devices.taco.DigitalInput',
                    tacodevice = nethost + 'pgaa/phytronixe/press1',
                   ),
    press2 = device('devices.taco.DigitalInput',
                    tacodevice = nethost + 'pgaa/phytronixe/press2',
                   ),
    sample  = device('devices.taco.motor.Motor',
                     tacodevice = nethost + 'pgaa/phytronixe/sample',
                     fmtstr = '%7.3f',
                     abslimits = (-5, 356),
                    ),
)


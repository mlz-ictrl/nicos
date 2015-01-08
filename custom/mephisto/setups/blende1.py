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

includes = ['system']

nethost = '//mephistosrv.mephisto.frm2/'

devices = dict(
    edge1 = device('devices.taco.Motor',
                   description = 'top edge',
                   tacodevice = nethost + 'mephisto/aperture1/motor1',
                   fmtstr = '%7.3f',
                   abslimits = (-100, 100),
                   lowlevel = True,
                   ),
    edge2 = device('devices.taco.Motor',
                   description = 'bottom edge',
                   tacodevice = nethost + 'mephisto/aperture1/motor2',
                   fmtstr = '%7.3f',
                   abslimits = (-100, 100),
                   lowlevel = True,
                   ),
    edge3 = device('devices.taco.Motor',
                   tacodevice = nethost + 'mephisto/aperture1/motor3',
                   fmtstr = '%7.3f',
                   abslimits = (-100, 100),
                   lowlevel = True,
                   ),
    edge4 = device('devices.taco.Motor',
                   tacodevice = nethost + 'mephisto/aperture1/motor4',
                   fmtstr = '%7.3f',
                   abslimits = (-100, 100),
                   lowlevel = True,
                   ),

    e1 = device('devices.generic.Axis',
                motor = 'edge1',
                coder = 'edge1',
                obs = None,
                precision = 0.1,
                lowlevel = True,
                ),
    e2 = device('devices.generic.Axis',
                motor = 'edge2',
                coder = 'edge2',
                obs = None,
                precision = 0.1,
                lowlevel = True,
                ),
    e3 = device('devices.generic.Axis',
                motor = 'edge3',
                coder = 'edge3',
                obs = None,
                precision = 0.1,
                lowlevel = True,
                ),
    e4 = device('devices.generic.Axis',
                motor = 'edge4',
                coder = 'edge4',
                obs = None,
                precision = 0.1,
                lowlevel = True,
                ),

    b1 = device('devices.generic.Slit',
                top = 'e1',
                bottom = 'e2',
                right = 'e3',
                left = 'e4',
                ),
)

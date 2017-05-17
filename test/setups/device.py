#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

name = 'test_device setup'

includes = ['stdsystem']

devices = dict(
    dev1 = device('test.test_simple.test_device.Dev1'),
    dev2_0 = device('test.test_simple.test_device.Dev2',
        attached = device('test.test_simple.test_device.Dev1'),
        attlist = [
            device('test.test_simple.test_device.Dev1'),
            device('test.test_simple.test_device.Dev1')
        ],
        param2 = 1,
        unit = 'mm',
        abslimits = (0, 10),
    ),
    dev2_1 = device('test.test_simple.test_device.Dev2',
        attached = 'dev1',
        param2 = 1,
        unit = 'mm',
        abslimits = (0, 10),
    ),
    dev2_2 = device('test.test_simple.test_device.Dev2',
        unit = 'mm',
    ),
    dev2_3 = device('test.test_simple.test_device.Dev2',
        attached = 'dev1',
        param2 = 1,
        unit = 'mm',
        abslimits = (0, 10),
    ),
    dev2_4 = device('test.test_simple.test_device.Dev2',
        failinit = True,
        attached = 'dev1',
        param2 = 1,
        unit = 'mm',
        abslimits = (0, 10),
    ),
    dev2_5 = device('test.test_simple.test_device.Dev2',
        failinit = True,
        failshutdown = True,
        attached = 'dev1',
        param2 = 1,
        unit = 'mm',
        abslimits = (0, 10),
    ),
    bus = device('test.test_simple.test_device.Bus',
        comtries = 3,
        comdelay = 0,
    ),
    mot = device('devices.generic.VirtualMotor',
        unit = 'deg',
        curvalue = 0,
        abslimits = (0, 10),
    ),
    privdev = device('devices.generic.VirtualMotor',
        requires = {'level': 'admin'},
        unit = 'mm',
        abslimits = (-50, 50),
        maxage = 0.0,  # no caching!
    ),
)

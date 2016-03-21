#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

name = 'simulation tests setup'

includes = []

from test.utils import getCacheNameAndPort

sysconfig = dict(
    cache = getCacheNameAndPort('localhost'),
    experiment = 'Exp',
)

devices = dict(
    Sample   = device('devices.tas.TASSample',
                     ),

    Exp      = device('nicos.devices.experiment.Experiment',
                      sample = 'Sample',
                      elog = False,
                      dataroot = 'test/root/data',
                      propprefix = 'p',
                      templates = '../../script_templates',
                      zipdata = True,
                      serviceexp = 'service',
                      lowlevel = False,
                      localcontact = 'M. Aintainer <m.aintainer@frm2.tum.de>',
                     ),

    motor    = device('nicos.devices.generic.VirtualMotor',
                      unit = 'deg',
                      initval = 0,
                      abslimits = (0, 5),
                     ),

    timer    = device('devices.generic.VirtualTimer',
                      lowlevel = True,
                     ),

    ctr1     = device('devices.generic.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 2000,
                      fmtstr = '%d',
                     ),

    det      = device('devices.generic.Detector',
                      timers = ['timer'],
                      monitors = [],
                      counters = ['ctr1'],
                      maxage = 3,
                      pollinterval = 0.5,
                     ),
)

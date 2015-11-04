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
# **************************************************************************

description = 'qmesydaq channel devices'

group = 'optional'

excludes = ['detector', 'sans', 'refsans']

nethost = 'taco61.ictrl.frm2'
qm = '//%s/test/qmesydaq/' % nethost

devices = dict(
    mon1   = device('devices.vendor.qmesydaq.Counter',
                    description = 'QMesyDAQ Counter0',
                    tacodevice = qm + 'counter0',
                    type = 'monitor',
                   ),
    mon2   = device('devices.vendor.qmesydaq.Counter',
                    description = 'QMesyDAQ Counter1',
                    tacodevice = qm + 'counter1',
                    type = 'monitor',
                   ),
    mon3   = device('devices.vendor.qmesydaq.Counter',
                    description = 'QMesyDAQ Counter2',
                    tacodevice = qm + 'counter2',
                    type = 'monitor',
                   ),
    mon4   = device('devices.vendor.qmesydaq.Counter',
                    description = 'QMesyDAQ Counter3',
                    tacodevice = qm + 'counter3',
                    type = 'monitor',
                   ),
    events = device('devices.vendor.qmesydaq.Counter',
                    description = 'QMesyDAQ Events channel',
                    tacodevice = qm + 'events',
                    type = 'counter',
                   ),
    timer  = device('devices.vendor.qmesydaq.Timer',
                    description = 'QMesyDAQ Timer',
                    tacodevice = qm + 'timer',
                   ),
    data   = device('devices.vendor.qmesydaq.MultiCounter',
                    description = 'QMesyDAQ Counter channels',
                    tacodevice = qm + 'det',
                   ),
    det    = device('devices.generic.Detector',
                    description = 'QMesyDAQ MultiChannel Detector',
                    timers = ['timer'],
                    counters = ['events', 'data'],
                    monitors = ['mon1', 'mon2', 'mon3', 'mon4'],
                   ),
)

startupcode = """
SetDetectors(det)
"""

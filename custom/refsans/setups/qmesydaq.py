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

description = 'qmesydaq devices for REFSANS'

# to be included by refsans ?
group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/qmesydaq' % nethost

devices = dict(
    BerSANSFileSaver  = device('sans1.bersans.BerSANSFileFormat',
                               description = 'Saves image data in BerSANS format',
                               filenametemplate = ['D%(counter)07d.001',
                                                   '/data_user/D%(counter)07d.001'],
                               flipimage = 'none',
                               lowlevel = True,
                              ),
    #~ LiveViewSink = device('nicos.devices.fileformats.LiveViewSink',
                               #~ description = 'Sends image data to LiveViewWidget',
                               #~ filenametemplate=[],
                               #~ lowlevel = True,
                              #~ ),
    mon1 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Counter0',
                     tacodevice = '%s/counter0' % tacodev,
                     type = 'monitor',
                     ),
    mon2 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     description = 'QMesyDAQ Counter1',
                     tacodevice = '%s/counter0' % tacodev,
                     type = 'monitor',
                     ),
    #~ qm_ctr2 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     #~ description = 'QMesyDAQ Counter2',
                     #~ tacodevice = '%s/counter2' % tacodev,
                     #~ type = 'monitor',
                     #~ ),
    #~ qm_ctr3= device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     #~ description = 'QMesyDAQ Counter3',
                     #~ tacodevice = '%s/counter3' % tacodev,
                     #~ type = 'monitor',
                     #~ ),
    #~ qm_ev  = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     #~ description = 'QMesyDAQ Events channel',
                     #~ tacodevice = '%s/events' % tacodev,
                     #~ type = 'counter',
                     #~ ),
    timer = device('nicos.devices.vendor.qmesydaq.QMesyDAQTimer',
                     description = 'QMesyDAQ Timer',
                     tacodevice = '%s/timer' % tacodev,
                     ),
    det    = device('nicos.devices.vendor.qmesydaq.QMesyDAQImage',
                     description = 'QMesyDAQ Image type Detector1',
                     tacodevice = '%s/det' % tacodev,
                     events = None,
                     timer = 'timer',
                     counters = [],
                     monitors = ['mon1', 'mon2'],
                     fileformats = ['BerSANSFileSaver'],
                     subdir = 'bersans',
                     ),
)

startupcode = """
SetDetectors(det)
"""

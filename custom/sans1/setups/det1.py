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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************

description = 'qmesydaq devices for SANS1'

# included by sans1
group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    BerSANSFileSaver  = device('sans1.bersans.BerSANSFileFormat',
                               description = 'Saves image data in BerSANS format',
                               filenametemplate = ['D%(counter)07d.001',
                                                   '/data_user/D%(counter)07d.001'],
                               flipimage = 'updown',
                               lowlevel = True,
                              ),
    #~ LiveViewSink = device('nicos.devices.fileformats.LiveViewSink',
                               #~ description = 'Sends image data to LiveViewWidget',
                               #~ filenametemplate=[],
                               #~ lowlevel = True,
                              #~ ),
    det1_mon1 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                       description = 'QMesyDAQ Counter0',
                       tacodevice = '//%s/sans1/qmesydaq/counter0' % nethost,
                       type = 'monitor',
                      ),
    det1_mon2 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                       description = 'QMesyDAQ Counter1',
                       tacodevice = '//%s/sans1/qmesydaq/counter1' % nethost,
                       type = 'monitor',
                      ),
    #~ qm_ctr2 = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     #~ description = 'QMesyDAQ Counter2',
                     #~ tacodevice = '//%s/sans1/qmesydaq/counter2' % nethost,
                     #~ type = 'monitor',
                     #~ ),
    #~ qm_ctr3= device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                     #~ description = 'QMesyDAQ Counter3',
                     #~ tacodevice = '//%s/sans1/qmesydaq/counter3' % nethost,
                     #~ type = 'monitor',
                     #~ ),
    det1_ev  = device('nicos.devices.vendor.qmesydaq.QMesyDAQCounter',
                      description = 'QMesyDAQ Events channel',
                      tacodevice = '//%s/sans1/qmesydaq/events' % nethost,
                      type = 'counter',
                     ),
    det1_timer = device('nicos.devices.vendor.qmesydaq.QMesyDAQTimer',
                        description = 'QMesyDAQ Timer',
                        tacodevice = '//%s/sans1/qmesydaq/timer' % nethost,
                       ),
    det1    = device('nicos.devices.vendor.qmesydaq.QMesyDAQImage',
                     description = 'QMesyDAQ Image type Detector1',
                     tacodevice = '//%s/sans1/qmesydaq/det' % nethost,
                     events = None,
                     timer = 'det1_timer',
                     counters = [],
                     monitors = ['det1_mon1', 'det1_mon2'],
                     fileformats = ['BerSANSFileSaver'],
                     subdir = 'bersans',
                    ),
)

startupcode = """
SetDetectors(det1)
"""

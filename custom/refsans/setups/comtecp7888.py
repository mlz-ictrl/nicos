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

description = 'devices for fast detector using comtec p7888 for REFSANS'

# to be included by refsans?
group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/fast' % nethost

devices = dict(
    RawFileSaver  = device('nicos.devices.fileformats.raw.SingleRAWFileFormat',
                               description = 'Saves image data in RAW format',
                               filenametemplate = ['%(proposal)s_%(counter)s.raw',
                                      '%(proposal)s_%(session.experiment.lastscan)s'
                                      '_%(counter)s_%(scanpoint)s.raw'],
                               lowlevel = True,
                              ),
    #~ LiveViewSink = device('nicos.devices.fileformats.LiveViewSink',
                               #~ description = 'Sends image data to LiveViewWidget',
                               #~ filenametemplate=[],
                               #~ lowlevel = True,
                              #~ ),
    fastctr_a = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel A of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_a' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_b = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel B of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_b' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_c = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel C of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_c' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_d = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel D of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_d' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_e = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel E of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_e' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_f = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel F of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_f' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_g = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel G of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_g' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    fastctr_h = device('nicos.devices.taco.detector.FRMCounterChannel',
                       description = "Channel H of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_h' % tacodev,
                       type = 'counter',
                       mode = 'normal',
                      ),
    # the following may not work as expected ! (or at all!)
    #~ comtec    = device('nicos.devices.vendor.qmesydaq.QMesyDAQImage',
                     #~ description = 'Comtep P7888 Fast Counter Main detector device',
                     #~ tacodevice = '%s/detector' % tacodev,
                     #~ events = None,
                     #~ timer = None,
                     #~ counters = ['fastctr_a','fastctr_b','fastctr_c','fastctr_d',
                                 #~ 'fastctr_e','fastctr_f','fastctr_g','fastctr_h'],
                     #~ monitors = None,
                     #~ fileformats = ['RawFileSaver'],
                     #~ subdir = 'fast',
                     #~ ),
)

startupcode = """
#~ SetDetectors(comtec)
"""

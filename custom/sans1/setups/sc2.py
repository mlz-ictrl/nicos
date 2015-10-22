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
#
# *****************************************************************************

description = 'sample table devices'

group = 'optional'

includes = ['sample_table_1'] # includes 'sample_table_1'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    samplenameselector = device('devices.generic.ParamDevice',
                                description = 'Paramdevice used to select the right samplename',
                                lowlevel = True,
                                device = 'Sample',
                                parameter = 'activesample',
                               ),

    sc2_y    = device('devices.generic.Axis',
                         description = 'Sample Changer 1/2 Axis',
                         pollinterval = 15,
                         maxage = 60,
                         fmtstr = '%.2f',
                         abslimits = (-0, 600),
                         precision = 0.01,
                         motor = 'sc2_ymot',
                         coder = 'sc2_yenc',
                         obs=[],
                        ),
    sc2_ymot = device('devices.taco.motor.Motor',
                         description = 'Sample Changer 1/2 Axis motor',
                         tacodevice = '//%s/sans1/samplechanger/y-sc1mot' % (nethost, ),
                         fmtstr = '%.2f',
                         abslimits = (-0, 600),
                         lowlevel = True,
                        ),
    sc2_yenc = device('devices.taco.coder.Coder',
                         description = 'Sample Changer 1/2 Axis encoder',
                         tacodevice = '//%s/sans1/samplechanger/y-sc1enc' % (nethost, ),
                         fmtstr = '%.2f',
                         lowlevel = True,
                        ),

    sc2    = device('devices.generic.MultiSwitcher',
                    description = 'Sample Changer 2 Huber device',
                    moveables = ['sc2_y', 'st1_z', 'samplenameselector'],
                    mapping = {1:  [592.5, -32, 1],  2: [533.5, -32, 2],
                               3:  [474.5, -32, 3],  4: [415.5, -32, 4],
                               5:  [356.5, -32, 5],  6: [297.5, -32, 6],
                               7:  [238.5, -32, 7],  8: [179.5, -32, 8],
                               9:  [120.5, -32, 9], 10: [ 61.5, -32, 10],
                               11: [  2.5, -32, 11],
                               12: [592.5,  27, 12], 13: [533.5,  27, 13],
                               14: [474.5,  27, 14], 15: [415.5,  27, 15],
                               16: [356.5,  27, 16], 17: [297.5,  27, 17],
                               18: [238.5,  27, 18], 19: [179.5,  27, 19],
                               20: [120.5,  27, 20], 21: [ 61.5,  27, 21],
                               22: [  2.5,  27, 22],
                               },
                    fallback = 0,
                    fmtstr = '%d',
                    precision = [0.05, 0.05, 100], # for use without nicos
                    #~ precision = [0.05, 0.05, 0], # for use with nicos
                    blockingmove = False,
                    lowlevel = False,
                   ),

    SampleChanger2 = device('devices.generic.DeviceAlias',
                           alias = 'sc2',
                          )
)

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
                    mapping = {1:  [594.5, -34, 1],  2: [535.5, -34, 2],
                               3:  [476.5, -34, 3],  4: [417.5, -34, 4],
                               5:  [358.5, -34, 5],  6: [299.5, -34, 6],
                               7:  [240.5, -34, 7],  8: [181.5, -34, 8],
                               9:  [122.5, -34, 9], 10: [ 63.5, -34, 10],
                               11: [  4.5, -34, 11],
                               12: [594.5,  25, 12], 13: [535.5,  25, 13],
                               14: [476.5,  25, 14], 15: [417.5,  25, 15],
                               16: [358.5,  25, 16], 17: [299.5,  25, 17],
                               18: [240.5,  25, 18], 19: [181.5,  25, 19],
                               20: [122.5,  25, 20], 21: [ 63.5,  25, 21],
                               22: [  4.5,  25, 22],
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

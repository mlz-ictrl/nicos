#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

includes = ['system', 'table']

nethost = '//sans1srv.sans1.frm2/'

devices = dict(
    sc1    = device('devices.taco.axis.Axis',
                    description = 'Sample Changer 1 Axis',
                    lowlevel = True,
                    tacodevice = nethost + 'sans1/samplechanger/y-sc1',
                    fmtstr = '%.2f',
                    abslimits = (-0, 600),
                   ),
    sc1_mot = device('devices.taco.motor.Motor',
                     description = 'Sample Changer 1 Motor',
                     lowlevel = True,
                     tacodevice = nethost + 'sans1/samplechanger/y-sc1mot',
                     fmtstr = '%.2f',
                     abslimits = (-0, 600),
                    ),
    sc1_enc = device('devices.taco.coder.Coder',
                     description = 'Sample Changer 1 Encoder',
                     lowlevel = True,
                     tacodevice = nethost + 'sans1/samplechanger/y-sc1enc',
                     fmtstr = '%.2f',
                    ),

    sc1_sw    = device('devices.generic..MultiSwitcher',
                       description = 'Sample Changer 1 Huber device',
                       moveables = ['sc1', 'z_2b'],
                       mapping = {'1':  [594.5, -31],  '2': [535.5, -31],
                                  '3':  [476.5, -31],  '4': [417.5, -31],
                                  '5':  [358.5, -31],  '6': [299.5, -31],
                                  '7':  [240.5, -31],  '8': [181.5, -31],
                                  '9':  [122.5, -31], '10': [ 63.5, -31],
                                  '11': [  4.5, -31],
                                  '12': [594.5,  28], '13': [535.5,  28],
                                  '14': [476.5,  28], '15': [417.5,  28],
                                  '16': [358.5,  28], '17': [299.5,  28],
                                  '18': [240.5,  28], '19': [181.5,  28],
                                  '20': [122.5,  28], '21': [ 63.5,  28],
                                  '22': [  4.5,  28],
                                  },
                       precision = [0.05, 0.05],
                       blockingmove = False,
                      ),
)


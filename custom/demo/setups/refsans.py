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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

description = 'REFSANS demo setup'

group = 'basic'

excludes = ['tas', 'sans',]

includes = []

devices = dict(
    Sample = device('devices.sample.Sample'),

    nok2_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 310),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok2_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 500),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok2 = device('refsans.virtual.NOK',
                  description = 'NOK 2',
                  left = 'nok2_r',
                  right = 'nok2_s',
                  length = 300,
                  ldist = 74.5,
                  rdist = 49,
                 ),

    nok3_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (205.5, 279.5),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok3_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (217.7, 283.7),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok3 = device('refsans.virtual.NOK',
                  description = 'NOK 3',
                  left = 'nok3_r',
                  right = 'nok3_s',
                  length = 600,
                  ldist = 151,
                  rdist = 149,
                 ),

    nok4_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (209.3, 278.3),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok4_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 500),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok4 = device('refsans.virtual.NOK',
                  description = 'NOK 4',
                  left = 'nok4_r',
                  right = 'nok4_s',
                  length = 1000,
                  ldist = 151,
                  rdist = 149,
                 ),

    nok5a_r  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 791.8),
                      speed = 5,
                      unit = 'mm',
                     ),
    nok5a_s  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 800),
                      speed = 5,
                      unit = 'mm',
                     ),
    nok5a = device('refsans.virtual.NOK',
                   description = 'NOK 5a',
                   left = 'nok5a_r',
                   right = 'nok5a_s',
                   length = 1720,
                   ldist = 689.5,
                   rdist = 249.7,
                  ),

    nok5b_r  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 1250),
                      speed = 5,
                      unit = 'mm',
                     ),
    nok5b_s  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 1250),
                      speed = 5,
                      unit = 'mm',
                     ),
    nok5b = device('refsans.virtual.NOK',
                   description = 'NOK 5b',
                   left = 'nok5b_r',
                   right = 'nok5b_s',
                   length = 1720,
                   ldist = 249.5,
                   rdist = 249.7,
                  ),

    nok6_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok6_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok6 = device('refsans.virtual.NOK',
                  description = 'NOK 6',
                  left = 'nok6_r',
                  right = 'nok6_s',
                  length = 1720,
                  ldist = 249.5,
                  rdist = 249,
                 ),

    nok7_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok7_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok7 = device('refsans.virtual.NOK',
                  description = 'NOK 7',
                  left = 'nok7_r',
                  right = 'nok7_s',
                  length = 1190,
                  ldist = 250,
                  rdist = 249.7,
                 ),

    nok8_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok8_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok8 = device('refsans.virtual.NOK',
                  description = 'NOK 8',
                  left = 'nok8_r',
                  right = 'nok8_s',
                  length = 880,
                  ldist = 249.5,
                  rdist = 249.7,
                 ),

    nok9_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok9_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (0, 1250),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok9 = device('refsans.virtual.NOK',
                  description = 'NOK 9',
                  left = 'nok9_r',
                  right = 'nok9_s',
                  length = 840,
                  ldist = 250,
                  rdist = 250,
                 ),

    LiveViewFileSink = device('devices.fileformats.LiveViewSink',
                              description = 'Sends image data to LiveViewWidget',
                             ),

    det      = device('devices.generic.virtual.Virtual2DDetector',
                      description = 'Virtual 2D detector',
                      fileformats = ['LiveViewFileSink'], # 'BerSANSFileSaver', 'RAWFileSaver'
                      distance = None, # 'det_pos1',
                      collimation = None, # 'guide',
                      subdir = '2ddata',
                     ),
)

startupcode = '''
SetDetectors(det)
printinfo("============================================================")
printinfo("Welcome to the NICOS REFSANS demo setup.")
printinfo("Run count(1) to collect an image.")
printinfo("============================================================")
'''

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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

name = 'test_puma setup'

includes = ['stdsystem']

devices = dict(
    phi = device('nicos_mlz.puma.devices.comb_ax.CombAxis',
                 motor = device('nicos.devices.generic.VirtualMotor',
                                unit = 'deg',
                                abslimits = (-5, 116.1),
                               ),
                 obs = [],
                 precision = 0.005,
                 offset = 0.,
                 maxtries = 5,
                 loopdelay = 0.02,
                 fix_ax = device('nicos.devices.generic.VirtualMotor',
                                 unit = 'deg',
                                 abslimits = (-15., 355.),
                                ),
                 iscomb = False,
                ),
    afpg = device('nicos_mlz.puma.devices.focus.FocusAxis',
                  motor = device('nicos.devices.generic.VirtualMotor',
                                 unit = 'deg',
                                 abslimits = (-55, 55),
                                ),
                  obs = [],
                  uplimit = 5,
                  lowlimit = -5,
                  flatpos = 4.92,
                  startpos = 4,
                  precision = 0.25,
                  maxtries = 15,
                  loopdelay = 0.02,
                 ),
    polyswitch = device('nicos.devices.generic.ManualSwitch',
                        states = [0, 1],
                       ),
    mtt = device('nicos_mlz.puma.devices.mtt.MttAxis',
                 motor = device('nicos.devices.generic.VirtualMotor',
                                unit = 'deg',
                                abslimits = (-110.1, 0),
                               ),
                 io_flag = 'polyswitch',
                 polyswitch = 'polyswitch',
                 obs = [],
                 precision = 0.011,
                 offset = 0.0,
                 maxtries = 1,
                 backlash = -0.1,
                 loopdelay = 0.02,
                 polysleep = 0.02,
                ),
)

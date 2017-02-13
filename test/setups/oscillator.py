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

name = 'test_oscillator setup'

includes = ['axis']

devices = dict(
    # Take range from the 'axis' device
    osci = device('devices.generic.Oscillator',
                  moveable = 'axis',
                 ),
    # Set own range and it is stoppable
    osci2 = device('devices.generic.Oscillator',
                   moveable = 'axis',
                   range = (0, 50),
                   stoppable = True,
                  ),
    # configured range outside the attached device limits
    osci3 = device('devices.generic.Oscillator',
                   moveable = 'axis',
                   range = (-110, 0),
                  ),
    osci4 = device('devices.generic.Oscillator',
                   moveable = 'axis',
                   range = (0, 110),
                  ),
)

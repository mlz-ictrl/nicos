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

description = 'Refsans_flipper special HW'

# not included by others
group = 'optional'

uribase = 'tango://refsans10.refsans.frm2:10000/refsans/flipper/'

devices = dict(
    guide = device('devices.tango.AnalogInput',
                   description = 'Temperature of Flipping Guide',
                   tangodevice = uribase + 'guide_temp',
                  ),
    coil = device('devices.tango.AnalogInput',
                  description = 'Temperature of Flipping Coil',
                  tangodevice = uribase + 'coil_temp',
                 ),
    current = device('devices.tango.WindowTimeoutAO',
                     description = 'Current of Flipping Coil',
                     tangodevice = uribase + 'current',
                     precision = 0.1,
                    ),
    frequency = device('devices.tango.AnalogInput',
                       description = 'Frequency of Flipping Field',
                       tangodevice = uribase + 'frequency',
                      ),
    flipper = device('devices.tango.NamedDigitalOutput',
                     description = 'Flipper',
                     tangodevice = uribase + 'flipper',
                     mapping = dict(ON=1, OFF=0),
                    ),
)

startupcode = """
"""


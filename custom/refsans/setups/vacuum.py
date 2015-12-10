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

description = 'Vacuum readout devices using Leybold Center 3'

# not included by others
group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/center' % nethost

devices = dict(
    vacuum_CB = device('devices.taco.AnalogInput',
                description = 'Pressure in Chopper chamber',
                tacodevice = '%s/center_0' % tacodev,
               ),
    vacuum_SFK = device('devices.taco.AnalogInput',
                 description = 'Pressure in beam guide chamber',
                 tacodevice = '%s/center_1' % tacodev,
                ),
    vacuum_SR = device('devices.taco.AnalogInput',
                description = 'Pressure in scattering tube',
                tacodevice = '%s/center_2' % tacodev,
               ),
)

startupcode = """
"""


#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

name = 'test_t2t setup'

includes = ['stdsystem']

devices = dict(
    omega  = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-180, 180),
        unit = 'deg',
    ),
    detarm = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-360, 360),
        unit = 'deg',
    ),
    t2t = device('nicos_mlz.jcns.devices.motor.MasterSlaveMotor',
        description = '2 theta axis moving detarm = 2 * omega',
        master = 'omega',
        slave = 'detarm',
        scale = 2.,
    ),
)

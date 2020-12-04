#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

name = 'test_pgaa setup'

includes = ['stdsystem']

devices = dict(
    ellipse = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        lowlevel = True,
    ),
    collimator = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        lowlevel = True,
    ),
    ellcol = device('nicos_mlz.pgaa.devices.BeamFocus',
        ellipse = 'ellipse',
        collimator = 'collimator',
        unit = '',
    ),
    samplemotor = device('nicos.devices.generic.VirtualMotor',
        abslimits = (1, 16),
        speed = 0,
        unit = '',
        curvalue = 1,
    ),
    pushactuator = device('nicos.devices.generic.ManualSwitch',
        states = ['down', 'up'],
        lowlevel = True,
    ),
    sensort = device('nicos_demo.vpgaa.devices.sampledevices.PushReader',
        moveable = 'pushactuator',
        inverse = True,
        lowlevel = True,
    ),
    sensorl = device('nicos_demo.vpgaa.devices.sampledevices.PushReader',
        moveable = 'pushactuator',
        lowlevel = True,
    ),
    push = device('nicos_mlz.pgaa.devices.sampledevices.SamplePusher',
        unit = '',
        actuator = 'pushactuator',
        sensort = 'sensort',
        sensorl = 'sensorl',
        lowlevel = True,
    ),
    sc = device('nicos_mlz.pgaa.devices.SampleChanger',
        motor = 'samplemotor',
        push = 'push',
        delay = 0.1,
    ),
    att1 = device('nicos.devices.generic.ManualSwitch',
        states = ['out', 'in'],
    ),
    att2 = device('nicos.devices.generic.ManualSwitch',
        states = ['out', 'in'],
    ),
    att3 = device('nicos.devices.generic.ManualSwitch',
        states = ['out', 'in'],
    ),
    att = device('nicos_mlz.pgaa.devices.Attenuator',
        description = 'Attenuator device',
        moveables = ['att1', 'att2', 'att3'],
        precision = None,
        unit = '%',
        fmtstr = '%.1f',
        mapping = {
            100.: ('out', 'out', 'out'),
            47.: ('out', 'in', 'out'),
        },
    ),
)

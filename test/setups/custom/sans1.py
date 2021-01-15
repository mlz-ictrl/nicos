#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.kruege@frm2.tum.de>
#
# *****************************************************************************

name = 'test_sans1 setup'


devices = dict(
    dev1 = device('nicos.devices.generic.virtual.VirtualMotor',
                  abslimits = (0, 100),
                  unit = 'a.u',
                 ),
    ieee1 = device('nicos_mlz.sans1.devices.bersans.IEEEDevice'),
    ieee2 = device('nicos_mlz.sans1.devices.bersans.IEEEDevice',
                   valuename = 'dev1'),
    ieee3 = device('nicos_mlz.sans1.devices.bersans.IEEEDevice',
                   valuename = 'dev1.curvalue'),
    det1_z_ax = device('nicos.devices.generic.Axis',
        fmtstr = '%.0f',
        maxage = 120,
        pollinterval = 5,
        precision = 1.0,
        dragerror = 150.0,
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (1100, 20000),
            curvalue = 1111,
            fmtstr = '%.1f',
            unit = 'mm',
        ),
    ),
    det1_z = device('nicos_mlz.sans1.devices.detector.DetectorTranslation',
        device = 'det1_z_ax',
        lock = device('nicos_mlz.sans1.devices.hv.VoltageSwitcher',
            moveable = device('nicos_mlz.sans1.devices.hv.Sans1HV',
                unit = 'V',
                fmtstr = '%d',
                supply = device('nicos.devices.generic.VirtualMotor',
                    abslimits = (0.0, 1501.0),
                    maxage = 120,
                    pollinterval = 15,
                    fmtstr = '%d',
                    unit = 'V',
                    speed = 10,
                ),
                discharger = device('nicos.devices.generic.ManualSwitch',
                    states = (0, 1),
                ),
                interlock = device('nicos.devices.generic.ManualSwitch',
                    states = (0, 1),
                ),
                maxage = 120,
                pollinterval = 15,
            ),
            mapping = {
                'ON': (1500, 1),
                'LOW': (1, 69),
                'OFF': (0, 1)
            },
            precision = 1,
            unit = '',
            fallback = 'unknown',
        ),
        unlockvalue = 'LOW',
        fmtstr = '%.0f',
        maxage = 120,
        pollinterval = 15,
    ),
)

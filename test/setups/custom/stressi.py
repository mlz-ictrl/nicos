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

name = 'test_stressi setup'

includes = ['stdsystem']

stressi_sinklist = ['csink']

try:
    import quickyaml  # pylint: disable=unused-import
    stressi_sinklist.append('ysink')
except Exception:
    try:
        import yaml  # pylint: disable=unused-import
        stressi_sinklist.append('ysink')
    except Exception:
        pass

sysconfig = dict(
    datasinks = stressi_sinklist,
)

devices = dict(
    tths = device('devices.generic.VirtualMotor',
        abslimits = (-180, 180),
        unit = 'deg',
    ),
    phis = device('devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-720, 720),
    ),
    chis = device('devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-180, 180),
    ),
    xt = device('devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-120, 120),
    ),
    yt = device('devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-120, 120),
    ),
    zt = device('devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-0, 300),
    ),
    omgm = device('devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-200, 200),
    ),
    tthm = device('devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (50, 100),
    ),
    slits = device('stressi.slit.Slit',
        left = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-26, 10),
        ),
        right = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-10, 26),
        ),
        bottom = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-43, 10),
        ),
        top = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-10, 43),
        ),
        opmode = 'centered',
    ),
    slitm = device('stressi.slit.TwoAxisSlit',
        horizontal = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 100),
        ),
        vertical = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 155),
        ),
    ),
    slitp = device('stressi.slit.TwoAxisSlit',
        horizontal = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 100),
        ),
        vertical = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 155),
        ),
    ),
    slite = device('devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (0, 70),
    ),
    transm = device('devices.generic.Switcher',
        moveable = device('devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-200, 200),
        ),
        mapping = {
            'Si': 0.292,
            'PG': 30.292,
            'Ge': 60.292,
        },
        precision = 0.01,
        unit = '',
    ),
    wav = device('stressi.wavelength.Wavelength',
        omgm = 'omgm',
        crystal = 'transm',
        plane = '',
        base = 'tthm',
        unit = 'AA',
        abslimits = (0.9, 2.5),
    ),
    mon1 = device('devices.generic.VirtualCounter',
        fmtstr = '%d',
        type = 'monitor',
        countrate = 1000.,
    ),
    tim1 = device('devices.generic.VirtualTimer',
        unit = 's',
    ),
    image = device('devices.generic.VirtualImage',
        fmtstr = '%d',
        sizes = (256, 256),
    ),
    adet = device('devices.generic.Detector',
        timers = ['tim1'],
        monitors = ['mon1'],
        counters = [],
        images = ['image'],
        maxage = 3,
        pollinterval = 0.5,
    ),
    ysink = device('nicos.stressi.datasinks.YamlDatafileSink',
        filenametemplate = ['m2%(scancounter)08d.yaml'],
        detectors = ['adet'],
    ),
    csink = device('nicos.stressi.datasinks.CaressScanfileSink',
        filenametemplate = ['m2%(scancounter)08d.dat'],
        detectors = ['adet'],
    ),
)

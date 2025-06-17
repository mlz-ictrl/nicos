# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
    tths = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-180, 180),
        unit = 'deg',
    ),
    phis = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-720, 720),
    ),
    chis = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-180, 180),
    ),
    xt = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-120, 120),
    ),
    yt = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-120, 120),
    ),
    zt = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-0, 300),
    ),
    omgm = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-200, 200),
    ),
    tthm = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (50, 100),
    ),
    slits = device('nicos.devices.generic.Slit',
        left = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-26, 10),
        ),
        right = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-10, 26),
        ),
        bottom = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-43, 10),
        ),
        top = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-10, 43),
        ),
        opmode = 'centered',
    ),
    slitm = device('nicos.devices.generic.TwoAxisSlit',
        horizontal = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 100),
        ),
        vertical = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 155),
        ),
    ),
    slitp = device('nicos.devices.generic.TwoAxisSlit',
        horizontal = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 100),
        ),
        vertical = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (0, 155),
        ),
    ),
    slite = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (0, 70),
    ),
    transm = device('nicos.devices.generic.Switcher',
        moveable = device('nicos.devices.generic.VirtualMotor',
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
    wav = device('nicos_mlz.stressi.devices.wavelength.Wavelength',
        omgm = 'omgm',
        crystal = 'transm',
        plane = '',
        base = 'tthm',
        unit = 'AA',
        abslimits = (0.9, 2.5),
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        fmtstr = '%d',
        type = 'monitor',
        countrate = 1000.,
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        unit = 's',
    ),
    strimage = device('nicos.devices.generic.VirtualImage',
        fmtstr = '%d',
        size = (64, 64),
        background = 0,
    ),
    adet = device('nicos.devices.generic.Detector',
        timers = ['tim1'],
        monitors = ['mon1'],
        images = ['strimage'],
        maxage = 3,
        pollinterval = 0.5,
    ),
    ysink = device('nicos_mlz.stressi.datasinks.YamlDatafileSink',
        filenametemplate = ['m2%(scancounter)08d.yaml'],
        detectors = ['adet'],
    ),
    csink = device('nicos_mlz.stressi.datasinks.CaressScanfileSink',
        filenametemplate = ['m2%(scancounter)08d.dat'],
        detectors = ['adet'],
    ),
    tthm_r = device('nicos_mlz.stressi.devices.wavelength.TransformedMoveable',
        dev = 'tthm',
        informula = '1./0.5 * x - 11.5 / 0.5',
        outformula = '0.5 * x + 11.5',
        precision = 0.001,
    ),
)

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

name = 'test_spodi setup'

includes = ['stdsystem']

sysconfig = dict(
    datasinks = ['spodisink', 'spodilivesink'],
)

devices = dict(
    tths = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-3.1, 170),
    ),
    omgs = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-360, 360),
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        fmtstr = '%d',
        type = 'monitor',
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        unit = 's',
    ),
    spodi_image = device('nicos_mlz.spodi.devices.VirtualImage',
        pollinterval = None,
        size = (80, 256),
        background = 0,
    ),
    basedet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim1'],
        monitors = ['mon1'],
        images = ['spodi_image'],
        maxage = 86400,
        pollinterval = None,
    ),
    adet = device('nicos_mlz.spodi.devices.Detector',
        motor = 'tths',
        detector = 'basedet',
        pollinterval = None,
        maxage = 86400,
        liveinterval = 5,
    ),
    spodisink = device('nicos_mlz.spodi.datasinks.CaressHistogram',
        filenametemplate = ['m1%(pointcounter)08d.ctxt'],
        detectors = ['adet'],
    ),
    spodilivesink = device('nicos_mlz.spodi.datasinks.LiveViewSink',
        correctionfile = 'nicos_mlz/spodi/data/detcorrection.dat',
    ),
    detsampledist = device('nicos.devices.generic.ManualMove',
        description = 'Distance between sample and detector',
        default = 1.117,
        abslimits = (1.117, 1.117),
        unit = 'm',
    ),
    omgm = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.3f',
        unit = 'deg',
        abslimits = (-10, 10),
        speed = 1,
    ),
    tthm = device('nicos.devices.generic.ManualSwitch',
        fmtstr = '%.3f',
        unit = 'deg',
        states = (155.,),
    ),
    wav = device('nicos_mlz.spodi.devices.Wavelength',
        unit = 'AA',
        omgm = 'omgm',
        tthm = 'tthm',
        crystal = 'crystal',
        plane = '551',
        fmtstr = '%.3f',
        abslimits = (0.5, 3.0),
    ),
    crystal = device('nicos.devices.generic.ManualSwitch',
        states = ['Ge',]
    ),
    samr = device('nicos.devices.generic.ManualSwitch',
        states = ('off', 'on'),
    ),
    sams_m = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-10, 370),
        speed = 5,
        unit = 'deg',
        visibility = (),
    ),
    sams = device('nicos_mlz.spodi.devices.SampleChanger',
        moveables = ['sams_m'],
        mapping = {
            'S1': [-3.04],
            'S2': [33.11],
            'S3': [68.8],
            'S4': [104.95],
            'S5': [140.93],
            'S6': [177.20],
            'S7': [212.91],
            'S8': [249.07],
            'S9': [285.11],
            'S10': [321.03],
        },
        fallback = '?',
        fmtstr = '%s',
        precision = [0.1],
        blockingmove = True,
        unit = '',
    ),
)

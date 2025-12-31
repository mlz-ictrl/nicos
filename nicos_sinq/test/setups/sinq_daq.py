# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************
description = 'Test setup for the SINQ-DAQ devices'

countprefix = 'SQ:SINQTEST:DAQ'

devices = dict(
    ElapsedTime = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = countprefix,
    ),
    DAQPreset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = '2nd Generation Data Acquisition',
        daqpvprefix = countprefix,
        channels = [],
        time_channel = ['ElapsedTime'],
    ),
    DAQ = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Interface',
        timers = ['ElapsedTime'],
        counters = [],
        monitors = ['DAQPreset'],
        images = [],
        others = [],
        liveinterval = 2,
        saveintervals = [2]
    ),
    ThresholdChannel = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThresholdChannel',
        daqpvprefix = countprefix,
        channels = [],
	visibility = {'metadata', 'namespace'},
    ),
    Threshold = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQMinThreshold',
        daqpvprefix = countprefix,
        min_rate_channel = 'ThresholdChannel',
	visibility = {'metadata', 'namespace'},
    ),
    Gate1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        daqpvprefix = countprefix,
        channel = 1,
	visibility = {'metadata', 'namespace'},
    ),
    Gate2 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQGate',
        daqpvprefix = countprefix,
        channel = 2,
	visibility = {'metadata', 'namespace'},
    ),
    TestGen = device('nicos_sinq.devices.epics.sinqdaq.DAQTestGen',
        daqpvprefix = countprefix,
	visibility = {'metadata', 'namespace'},
    ),
)

for i in range(10):
    devices[f'monitor{i+1}'] = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = f'Monitor {i + 1}',
        daqpvprefix = countprefix,
        channel = i + 1,
        type = 'monitor',
    )
    devices['DAQPreset'][1]['channels'].append(f'monitor{i+1}')
    devices['ThresholdChannel'][1]['channels'].append(f'monitor{i+1}')
    devices['DAQ'][1]['monitors'].append(f'monitor{i+1}')

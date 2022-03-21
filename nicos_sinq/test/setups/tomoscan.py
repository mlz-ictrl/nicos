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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from os import path

from test.utils import module_root, runtime_root

description = 'Setup for SINQ Tomography scan test'

name = 'Test SINQ tomography scanning setup'

includes = ['axis', 'detector']

devices = dict(
    motor2 = device('nicos.devices.generic.VirtualMotor',
        description = 'Test motor',
        unit = 'deg',
        curvalue = 0,
        abslimits = (0, 360),
    ),
    Exp = device('nicos_sinq.devices.experiment.TomoSinqExperiment',
        description = ' SINQ Tomo Experiment',
        sample = 'Sample',
        elog = True,
        dataroot = path.join(runtime_root, 'data'),
        propprefix = 'p',
        templates = path.join(module_root, 'test', 'script_templates'),
        zipdata = True,
    ),
    img_index = device('nicos.devices.generic.manual.ManualMove',
        description = 'Keeps the index of the last measured image',
        unit = '',
        abslimits = (0, 1e9),
        visibility = (),
    ),
)

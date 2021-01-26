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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""TREFF mirror sample device."""

import glob
from os import path

from nicos import config
from nicos.core import Param, oneof
from nicos.core.params import floatrange
from nicos.devices.sample import Sample


# get paths for rflfiles (*.rfl)
rfldir_paths = [
    path.join(config.setup_package_path, p.strip(), 'rflfiles')
    for p in config.setup_subdirs.split(',')
]

rfl_files = []
for p in rfldir_paths:
    rfl_files.extend(glob.glob(path.join(p, '*.rfl')))

# map filenames to full-qualified path, later definitions overwrite earlier ones
rfl_filenames = dict((path.basename(p), p) for p in rfl_files)


class MirrorSample(Sample):

    parameters = {
        'length': Param('Length of the mirror',
                        type=floatrange(0), settable=True, userparam=True,
                        unit='mm', default=200),
        'thickness': Param('Thickness of the mirror',
                           type=floatrange(0), settable=True, userparam=True,
                           unit='mm', default=8),
        'height': Param('Height of the mirror',
                        type=floatrange(0), settable=True, userparam=True,
                        unit='mm', default=32),
        'm': Param('Reflection index (m)',
                   type=floatrange(1), settable=True, userparam=True,
                   unit='', default=2),
        'alfa': Param('Linear decrease of reflectivity m > 1',
                      type=floatrange(0), settable=True, userparam=True,
                      unit='', default=4.25),
        'waviness': Param('Waviness of the mirror surface',
                          type=floatrange(0), settable=True, userparam=True,
                          unit='deg', default=0.01),
        'rflfile': Param('Reflectivity file',
                         type=oneof(None, *rfl_filenames), settable=True,
                         userparam=True, default=None),
    }

    def getReflectivityFile(self):
        return rfl_filenames.get(self.rflfile, None)

    def _applyParams(self, number, parameters):
        """Apply sample parameters.
        """
        Sample._applyParams(self, number, parameters)
        if 'length' in parameters:
            self.length = parameters['length']
        if 'thickness' in parameters:
            self.thickness = parameters['thickness']
        if 'height' in parameters:
            self.height = parameters['height']
        if 'm' in parameters:
            self.m = parameters['m']
        if 'alfa' in parameters:
            self.alfa = parameters['alfa']
        if 'waviness' in parameters:
            self.waviness = parameters['waviness']
        if 'rflfile' in parameters:
            self.rflfile = parameters['rflfile']

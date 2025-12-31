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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""VStressi detector image based on McSTAS simulation."""

import numpy as np

from nicos.core import Attach, Override, Param, Readable, oneof, tupleof
from nicos.core.constants import FINAL, LIVE, MASTER
from nicos.devices.mcstas import MIN_RUNTIME, McStasCounter as BaseCounter, \
    McStasImage, McStasSimulation as BaseSimulation

from nicos_virt_mlz.stressi.devices.sample import Sample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='stressi_fast'),
        'neutronspersec': Override(default={'localhost': 1.12e5}),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'xprime': Attach('Primary slit width', Readable),
        'yprime': Attach('Primary slit height', Readable),
        'l_ambda': Attach('Wave length', Readable),
        'xpos': Attach('Sample position x', Readable),
        'ypos': Attach('Sample position y', Readable),
        'zpos': Attach('Sample position z', Readable),
        'phi': Attach('Sample phi rotation', Readable, optional=True),
        'chi': Attach('Sample chi rotation', Readable, optional=True),
        'omega': Attach('Sample omega rotation', Readable),
        'theta2': Attach('Rotation of detector around the sample', Readable),
        'force': Attach('Force of the tensile rig', Readable, optional=True),
    }

    def _prepare_params(self):
        return [
            'xprime=%s' % self._dev_value(self._attached_xprime, 2 * 1000),
            'yprime=%s' % self._dev_value(self._attached_yprime, 2 * 1000),
            'primeswitch=1',
            'lambda=%s' % self._dev_value(self._attached_l_ambda),
            'xpos=%s' % self._dev_value(self._attached_xpos, 1000),
            'ypos=%s' % self._dev_value(self._attached_ypos, 1000),
            'zpos=%s' % self._dev_value(self._attached_zpos, 1000),
            'phi=%s' % self._dev_value(self._attached_phi),
            'chi=%s' % self._dev_value(self._attached_chi),
            'omega=%s' % self._dev_value(self._attached_omega),
            'theta2=%s' % self._dev_value(self._attached_theta2),
            'force=%s' % self._dev_value(self._attached_force),
            'sampleswitch=%d' % self._attached_sample.sampletype,
        ]


class Image(McStasImage):

    parameters = {
        'pixel_size': Param('Size of a single pixel (in mm)',
                            type=tupleof(float, float), volatile=False,
                            settable=False, default=(0.85, 0.85), unit='mm',
                            category='instrument'),
        'neutron_section': Param("Section to take 'neutrons' from PSD file",
                                 type=oneof('Data', 'Events'), mandatory=False,
                                 default='Events'),
    }

    def _readpsd(self, quality):
        if self._attached_mcstas._signal_sent or quality == FINAL:
            try:
                blocks = 1 if self.neutron_section == 'Events' else 3
                with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                    lines = f.readlines()[-blocks * (self.size[1] + 1):]
                if lines[0].startswith(f'# {self.neutron_section}') and \
                   self.mcstasfile in lines[0]:
                    factor = 1 if blocks == 1 else self._attached_mcstas._getScaleFactor()
                    buf = factor * np.loadtxt(lines[1:self.size[1] + 1],
                                              dtype=np.float32)
                    self._buf = buf.astype(self.image_data_type)
                    self.readresult = [self._buf.sum()]
                    self.log.debug('Read result: %s', self.readresult)
                elif quality != LIVE:
                    raise OSError('Did not find start line: %s' % lines[0])
            except OSError:
                if quality != LIVE:
                    self.log.exception('Could not read result file', exc=1)
        else:
            self.readresult = [0]
            self._buf = np.zeros(self.size).astype(self.image_data_type)


class McStasCounter(BaseCounter):

    def doRead(self, maxage=0):
        if self._mode == MASTER:
            try:
                with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                    line = list(f)[-1]
                    self.curvalue = float(line.split()[2])
            except Exception:
                if self._attached_mcstas._getTime() > MIN_RUNTIME:
                    self.log.warning('could not read result file', exc=1)
                self.curvalue = 0
        return self.curvalue

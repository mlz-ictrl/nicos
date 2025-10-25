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

"""VBIODIFF detector image based on McSTAS simulation."""

import re
from math import log10

import numpy as np

from nicos.core import Attach, Override, Readable
from nicos.devices.mcstas import DetectorMixin, McStasImage as BaseImage, \
    McStasSimulation as BaseSimulation
from nicos.devices.sxtal.sample import SXTalSample

from nicos_mlz.biodiff.devices.detector import BiodiffDetector


class McStasSimulation(BaseSimulation):

    parameter_overrides = {
        'mcstasprog': Override(default='biodiff_fast'),
        'neutronspersec': Override(default={'localhost': 2.3e4}),
    }

    attached_devices = {
        'sample': Attach('Mirror sample', SXTalSample),
        's1': Attach('Slit 1', Readable),
        's2': Attach('Slit 2', Readable),
        'omega': Attach('Sample omega rotation', Readable),
        'wavelength': Attach('Incoming wavelength', Readable),
        # 'sample_x': Attach('Sample position x', Readable),
        # 'sample_y': Attach('Sample position y', Readable),
        # 'sample_z': Attach('Sample position z', Readable),
        # 'beamstop': Attach('Beamstop position', Readable),
    }

    def _dev(self, dev, scale=1, default='0', fmtstr=None):
        if not dev:
            return default
        if not fmtstr:
            fmtstr = dev.fmtstr
        if scale > 1:
            sf = int(log10(scale))
            expr = re.compile(r'(?<=\.)\d+')
            nums = re.findall(expr, fmtstr)
            if nums:
                num = int(nums[0]) + sf
                m = re.search(expr, fmtstr)
                fmtstr = '%s%d%s' % (fmtstr[:m.start()], num, fmtstr[m.end()])
        return fmtstr % (dev.read(0) / scale)

    def _prepare_params(self):
        sample = self._attached_sample
        return [
            # SLIT_S1         (double) [default='5']
            'SLIT_S1=%s' % self._dev(self._attached_s1),
            # SLIT_S2         (double) [default='3']
            'SLIT_S2=%s' % self._dev(self._attached_s2),
            # omega           (double) [default='0.0']
            'omega=%s' % self._dev(self._attached_omega),
            # cell_a          (double) [default='80.0']
            'cell_a=%s' % sample.a,
            # cell_b          (double) [default='80.0']
            'cell_b=%s' % sample.b,
            # cell_c          (double) [default='80.0']
            'cell_c=%s' % sample.c,
            # Lam             (double) [default='2.68']
            'Lam=%s' % self._dev(self._attached_wavelength),
            # dLam            (double) [default='0.05']
            'dLam=%s' % 0.05,
            # REP             (double) [default='1000']
            'REP=%d' % 1000,
        ]


class McStasImage(BaseImage):

    image_data_type = np.uint16


class Detector(DetectorMixin, BiodiffDetector):
    pass

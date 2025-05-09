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

from nicos.core import Attach, Override, Readable
from nicos.devices.mcstas import DetectorMixin, \
    McStasSimulation as BaseSimulation
from nicos.devices.sxtal.sample import SXTalSample

from nicos_mlz.biodiff.devices.detector import BiodiffDetector


class McStasSimulation(BaseSimulation):

    parameter_overrides = {
        'mcstasprog': Override(default='biodiff_fast'),
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

    def _prepare_params(self):
        params = []
        params.append('SLIT_S1=%s' % self._attached_s1.read(0))
        params.append('SLIT_S2=%s' % self._attached_s2.read(0))
        params.append('omega=%s' % self._attached_omega.read(0))
        sample = self._attached_sample
        params.append('cell_a=%s' % sample.a)
        params.append('cell_b=%s' % sample.b)
        params.append('cell_c=%s' % sample.c)
        params.append('Lam=%s' % self._attached_wavelength.read(0))
        params.append('dLam=%s' % 0.05)
        params.append('REP=%s' % 1000)
        return params


class Detector(DetectorMixin, BiodiffDetector):
    pass

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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Puma detector image based on McSTAS simulation."""

from nicos.core.constants import SLAVE
from nicos.core.device import Readable
from nicos.core.params import Attach, Override
from nicos.devices.mcstas import MIN_RUNTIME, McStasCounter, \
    McStasSimulation as BaseSimulation
from nicos.devices.tas import TAS, Energy, TASSample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='puma_fast'),
        'neutronspersec': Override(default={'localhost': 1241000}),
    }

    attached_devices = {
        'tas': Attach('Spectrometer', TAS),
        'ef': Attach('Outgoing energy', Energy),
        'ei': Attach('Incoming energy', Energy),
        'sample': Attach('Sample', TASSample),
        'primary_collimation': Attach('Primary collimation', Readable),
    }

    Ki_Fix = 0,

    # NMO_installed = 0,  # 1 is vertical, 2 is horizontal, 3 is both

    # ResSampleName = "Resolution_Sample",

    # NMO parts

    # b0 = 0.2076,
    # mf = 100,
    # mb = 0,
    # mirror_width= 0.003,
    # collimator_mirror_distance = 0.1,  # distance from collimator to NMO array
    # focal_length = 1,
    # int mirrors = 80,
    # mirror_sidelength = 0.06,
    # lStart = -0.075,
    # lEnd = 0.075,
    # string rs_at_zero_str = "NULL",
    # string mirror_array_str = "NULL",  # PUMA_NMO_VerticalFocusing.txt",
    # bl_hgap = 0.06,
    # bl_vgap = 0.06

    def _dev(self, dev, scale=1):
        return dev.fmtstr % (float(dev.read(0)) / scale)

    def _prepare_params(self):
        q = self._attached_tas.read(0)
        pc = self._attached_primary_collimation.read(0)
        params = [
            'Ki_Fix=%s' % {'CKI': 0, 'CKF': 1}.get(self._attached_tas.scanmode, 0),
            'EFixed=%s' % self._dev(
                self._attached_ei if self._attached_tas.scanmode == 'CKI' else
                self._attached_ef),
            # 1000 is default for open, can be 20, 40 or 60 otherwise
            'primary_collimation=%s' % ('1000' if pc == 'closed' else pc),
            'qx=%s' % q[0],
            'qy=%s' % q[1],
            'qz=%s' % q[2],
            'deltaE=%s' % q[3],
            'lattice_a=%s' % self._attached_sample.lattice[0],
            'lattice_b=%s' % self._attached_sample.lattice[0],
            'lattice_c=%s' % self._attached_sample.lattice[0],
        ]

        # 'NMO_installed=%s' % 0, //1 is vertical, 2 is horizontal, 3 is both
        # 'ResSampleName=%s' % '"Resolution_Sample"',

        # NMO parts

        # 'b0= %s' % 0.2076,
        # 'mf=%s' % 100,
        # 'mb=%s' % 0,
        # 'mirror_width=%s' % 0.003,
        # distance from collimator to NMO array
        # 'collimator_mirror_distance=%s' % 0.1,
        # 'focal_length=%s' % 1,
        # 'mirrors=%s' %  80,
        # 'mirror_sidelength=%s' %  0.06,
        # 'lStart=%s' % -0.075,
        # 'lEnd=%s' % 0.075,
        # 'rs_at_zero_str=%s' % '"NULL"',
        # 'mirror_array_str=%s' % '"NULL"',  # PUMA_NMO_VerticalFocusing.txt",
        # 'bl_hgap=%s' % 0.06,
        # 'bl_vgap=%s' % 0.06

        return params


class Counter(McStasCounter):

    def doRead(self, maxage=0):
        if self._mode == SLAVE:
            return self.curvalue
        try:
            with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                for line in f:
                    if line.startswith('# values:'):
                        value = float(line.split()[4])
        except Exception:
            if self._attached_mcstas._getTime() > MIN_RUNTIME:
                self.log.warning('could not read result file', exc=1)
            value = 0
        self.curvalue = value * self.intensityfactor
        return self.curvalue

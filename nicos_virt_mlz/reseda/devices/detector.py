#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

"""Reseda detector image based on McSTAS simulation."""

from pathlib import Path

import numpy as np

from nicos.core.constants import LIVE
from nicos.core.device import Readable
from nicos.core.params import ArrayDesc, Attach, Override, Param, intrange, \
    oneof, tupleof
from nicos.devices.mcstas import McStasImage as BaseImage, \
    McStasSimulation as BaseSimulation

from nicos_virt_mlz.reseda.devices.sample import Sample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='reseda_fast'),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'l_ambda': Attach('Wave length', Readable),
        'd_lambda': Attach('Delta in wave length', Readable),
        'tablex': Attach('Sample position x', Readable),
        'tabley': Attach('Sample position y', Readable),
        'tablez': Attach('Sample position z', Readable),
        'table_rotx': Attach('Sample goniometer x', Readable),
        'table_roty': Attach('Sample goniometer y', Readable),
        'table_rotz': Attach('Sample goniometer z', Readable),
        'l1': Attach('Length between rf-flippers', Readable, optional=True),
        'l2': Attach('Length between second rf-flipper and detector',
                     Readable, optional=True),
        'coil_nse_len': Attach('Length of nse-coil', Readable, optional=True),
        'detectorangle': Attach('Rotation of detector around the sample',
                                Readable),
        'i_nse': Attach('Current of NSE-Coil', Readable),
        'om0': Attach('Frequency of first rf-flipper',
                      Readable, optional=True),
        'om1': Attach('Frequency of second rf-flipper',
                      Readable, optional=True),
    }

    def _dev(self, dev, scale=1):
        return dev.fmtstr % (dev.read(0) / scale)

    def _prepare_params(self):
        params = [
            'lam=%s' % self._dev(self._attached_l_ambda),
            'dlam=%s' % self._dev(self._attached_d_lambda, 100),
            # 'table_x=%s' % self._dev(self._attached_tablex),
            # 'table_y=%s' % self._dev(self._attached_tabley),
            # 'table_z=%s' % self._dev(self._attached_tablez),
            # 'table_rotx=%s' % self._dev(self._attached_table_rotx),
            # 'table_roty=%s' % self._dev(self._attached_table_roty),
            # 'table_rotz=%s' % self._dev(self._attached_table_rotz),
            'Inse=%s' % self._dev(self._attached_i_nse),
            'detectorangle=%s' % self._dev(self._attached_detectorangle),
            'samplenum=%d' % self._attached_sample.sampletype,
        ]
        if self._attached_l1:
            params.append('l1=%s' % self._dev(self._attached_l1))
        if self._attached_l2:
            params.append('l2=%s' % self._dev(self._attached_l2))
        if self._attached_coil_nse_len:
            params.append('coilnselen=%s' % self._dev(
                self._attached_coil_nse_len))
        if self._attached_om0:
            params.append('om0=%s' % self._dev(self._attached_om0))
        if self._attached_om1:
            params.append('om1=%s' % self._dev(self._attached_om1))
        return params

    def _getNeutronsToSimulate(self):
        n = self.neutronspersec * self.preselection
        if self._attached_sample.sampletype == 1:
            # Scaling factor for simulation runs with different sample types
            # determined by test runs
            n /= (85 / 70)
        return n


class McStasImage(BaseImage):
    """Image channel based on McStas simulation."""

    parameters = {
        'mode': Param('Data acquisition mode (tof or image)',
                      type=oneof('image', 'tof'), settable=True,
                      category='presets'),
        'tofchannels': Param('Total number of TOF channels to use',
                             type=intrange(1, 1024), default=128,
                             settable=True, internal=True,
                             category='presets'),
    }

    parameter_overrides = {
        'size': Override(type=tupleof(intrange(1, 32), intrange(1, 64),
                                      intrange(1, 8192), intrange(1, 8192)),
                         default=(6, 16, 128, 128), mandatory=False),
        'mcstasfile': Override(default='cascade.bin', mandatory=False),
    }

    _datashape = []

    def doInit(self, mode):
        if self.mode == 'image':
            self.arraydesc = ArrayDesc(
                'data', self._datashape, '<u4', ['X', 'Y'])
        else:
            self.arraydesc = ArrayDesc(
                'data', self._datashape, '<u4', ['X', 'Y', 'T'])

    def _readpsd(self, quality):
        try:
            def import_cascade_bin(path_to_result_dir):
                """Return a 'self.size' numpy array."""
                p = Path(path_to_result_dir).joinpath(self.mcstasfile)
                if p.exists():
                    return np.squeeze(np.fromfile(
                        str(p), dtype=np.dtype(np.double, self.size)))
                return np.zeros(self.size)

            factor = self._attached_mcstas._getScaleFactor()
            if hasattr(self._attached_mcstas, '_mcstasdirpath'):
                buf = import_cascade_bin(self._attached_mcstas._mcstasdirpath)
                self._buf = (buf * factor).astype(np.uint32)
            else:
                self._buf = np.zeros(self.size)
            self.readresult = [self._buf.sum()]
        except OSError:
            if quality != LIVE:
                self.log.exception('Could not read result file', exc=1)

    def doUpdateMode(self, value):
        self.tofchannels = np.prod(self.size[:2])
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and self.size[2:] or (
            (self.tofchannels, ) + self.size[2:])
        self._tres = (value == 'image') and 1 or self.tofchannels

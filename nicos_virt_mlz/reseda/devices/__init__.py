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
#
# *****************************************************************************

import numpy as np

from nicos.core.params import ArrayDesc, Param, Value, intrange, listof, \
    oneof, tupleof
from nicos.devices.generic import VirtualImage
from nicos.protocols.cache import FLAG_NO_STORE

from nicos_mlz.reseda.utils import MiezeFit


class CascadeDetector(VirtualImage):

    _perfoil = 16

    fitter = MiezeFit()

    parameters = {
        'mode': Param('Data acquisition mode (tof or image)',
                      type=oneof('tof', 'image'), settable=True,
                      default='image', category='presets'),
        'roi': Param('Region of interest, given as (x1, y1, x2, y2)',
                     type=tupleof(int, int, int, int),
                     default=(-1, -1, -1, -1), settable=True),
        'tofchannels': Param('Total number of TOF channels to use',
                             type=intrange(1, 1024), default=128,
                             settable=True, category='presets'),
        'foilsorder': Param('Usable foils, ordered by number.',
                            type=listof(intrange(0, 31)), settable=False,
                            default=[0, 1, 2, 3, 4, 5, 6, 7],
                            category='instrument'),
        'fitfoil': Param('Foil for contrast fitting (number BEFORE '
                         'resorting)',
                         type=int, default=0, settable=True),
    }

    def doInit(self, mode):
        self._buf = self._generate(0).astype('<u4')

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and self.sizes or \
            (self._perfoil * len(self.foilsorder), ) + self.sizes
        # (self.tofchannels,)
        self._tres = (value == 'image') and 1 or self.tofchannels

    def doStart(self):
        self.readresult = [0, 0]
        VirtualImage.doStart(self)

    def valueInfo(self):
        if self.mode == 'tof':
            return (Value(self.name + '.roi', unit='cts', type='counter',
                          errors='sqrt', fmtstr='%d'),
                    Value(self.name + '.total', unit='cts', type='counter',
                          errors='sqrt', fmtstr='%d'),
                    Value('fit.contrast', unit='', type='other',
                          errors='next', fmtstr='%.3f'),
                    Value('fit.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('fit.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('fit.avgErr', unit='', type='error',
                          errors='none', fmtstr='%.1f'),
                    Value('roi.contrast', unit='', type='other',
                          errors='next', fmtstr='%.3f'),
                    Value('roi.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('roi.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('roi.avgErr', unit='', type='error',
                          errors='none', fmtstr='%.1f'))
        return (Value(self.name + '.roi', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),
                Value(self.name + '.total', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'))

    @property
    def arraydesc(self):
        if self.mode == 'image':
            return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y'])
        return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y', 'T'])

    def doReadArray(self, quality):
        # get current data array from detector, reshape properly
        data = VirtualImage.doReadArray(self, quality)
        # determine total and roi counts
        total = data.sum()
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = data[..., y1:y2, x1:x2].sum()
        else:
            x1, y1, x2, y2 = 0, 0, data.shape[-1], data.shape[-2]
            roi = total

        if self.mode == 'image':
            self.readresult = [roi, total]
            return data

        data = np.array([data] * self._datashape[0])

        # demux timing into foil + timing
        nperfoil = self._datashape[0] // len(self.foilsorder)
        shaped = data.reshape(
            (len(self.foilsorder), nperfoil) + self._datashape[1:])
        # nperfoil = self.tofchannels // self.foils
        # shaped = data.reshape((self.foils, nperfoil) + self._datashape[1:])

        x = np.arange(nperfoil)

        ty = shaped[self.fitfoil].sum((1, 2))
        ry = shaped[self.fitfoil, :, y1:y2, x1:x2].sum((1, 2))

        self.log.debug('fitting %r and %r' % (ty, ry))

        self.readresult = [
            roi, total,
        ]

        # also fit per foil data and pack everything together to be send
        # via cache for display
        payload = []
        for foil in self.foilsorder:
            foil_tot = shaped[foil].sum((1, 2))
            foil_roi = shaped[foil, :, y1:y2, x1:x2].sum((1, 2))
            tres = self.fitter.run(x, foil_tot, None)
            rres = self.fitter.run(x, foil_roi, None)
            payload.append([tres._pars[1], tres._pars[2], foil_tot.tolist(),
                            rres._pars[1], rres._pars[2], foil_roi.tolist()])

        self._cache.put(self.name, '_foildata', payload, flag=FLAG_NO_STORE)
        return data

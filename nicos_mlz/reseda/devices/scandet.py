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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

import numpy as np

from nicos.core import Override, Param, Value, floatrange, oneof
from nicos.devices.generic import ScanningDetector as NicosScanDet

from nicos.devices.vendor.cascade import fit_a_sin


class ScanningDetector(NicosScanDet):
    """Reseda scanning detector."""

    parameters = {
        'echopoints': Param('Number of echo points',
                            type=oneof(4, 19), default=4, settable=True,
                            userparam=True),
        'echostep': Param('Current difference between points',
                          type=floatrange(0), default=0.1, settable=True,
                          userparam=True),
        'echostart': Param('starting current value for the phase coil',
                           type=float, default=0, userparam=True,
                           settable=True),
    }

    parameter_overrides = {
        'positions': Override(settable=False, volatile=True),
    }

    def _processDataset(self, dataset):
        for det in dataset.detectors:
            for imgdet in det._attached_images:
                if getattr(imgdet, 'mode', None) == 'image':
                    # extract roi.counts
                    roivalues = []
                    scanvalues = []
                    for subset in dataset.subsets:
                        for i, val in enumerate(subset.detvalueinfo):
                            if val.name.endswith('.roi'):
                                roivalues.append(subset.detvaluelist[i])
                                break
                        scanvalues.append(subset.devvaluelist[0])
                    # ofs, ampl, freq, phase
                    popt, perr, msg = fit_a_sin(scanvalues, roivalues)
                    if msg:
                        self.log.warning(msg)
                    return [abs(popt[1]), perr[1], popt[0], perr[0]]
        res = []
        for ctr in self._attached_detector._attached_counters:
            x = []
            y = []
            for subset in dataset.subsets:
                for i, val in enumerate(subset.detvalueinfo):
                    if val.name == ctr.name:
                        y.append(subset.detvaluelist[i])
                        x.append(subset.devvaluelist[0])
                        break
            # ofs, ampl, freq, phase
            popt, perr, msg = fit_a_sin(x, y)
            if msg:
                self.log.warning(msg)
            res.extend([abs(popt[1]), perr[1], popt[0], perr[0]])
        return res

    def doReadPositions(self):
        return self._calc_currents(self.echopoints, self.echostep,
                                   self.echostart)

    def _calc_currents(self, n, echostep=0.1, startval=0):
        return (startval +
                np.arange(-n // 2 + 1, n // 2 + 1, 1) * echostep).tolist()

    def valueInfo(self):
        res = []
        for imgdet in self._attached_detector._attached_images:
            if getattr(imgdet, 'mode', None) in ['image']:
                return (Value('fit.contrast', unit='', type='other',
                              errors='next', fmtstr='%.3f'),
                        Value('fit.contrastErr', unit='', type='error',
                              errors='none', fmtstr='%.3f'),
                        Value('fit.avg', unit='', type='other', errors='next',
                              fmtstr='%.1f'),
                        Value('fit.avgErr', unit='', type='error',
                              errors='none', fmtstr='%.1f'))
        res = []
        for ctr in self._attached_detector._attached_counters:
            res.append(Value('%s.fit.contrast' % ctr.name, unit=ctr.unit,
                             type='other', errors='next', fmtstr='%.3f'))
            res.append(Value('%s.fit.contrastErr' % ctr.name, unit=ctr.unit,
                             type='error', errors='none', fmtstr='%.3f'))
            res.append(Value('%s.fit.avg' % ctr.name, unit=ctr.unit,
                             type='other', errors='next', fmtstr='%.1f'))
            res.append(Value('%s.fit.avgErr' % ctr.name, unit=ctr.unit,
                             type='error', errors='none', fmtstr='%.1f'))
        return tuple(res)

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Override, Value
from nicos.utils.fitting import curve_fit
from nicos.devices.generic import ScanningDetector as NicosScanDet

#from nicos_mlz.mira.devices.cascade_win import CascadeDetector as MiraCascadeDetector
from nicos_mlz.mira.devices.cascade import CascadeDetector as MiraCascadeDetector


def fit_a_sin(x, y):
    perr = 4*[float('inf')]
    if len(x) != len(y):
        return 4*[0], 4*[0], 'need equal number of x and y values!'
    if len(y) == 1:
        startpar = [y[0], 0, 1, 0]
    else:
        startpar = [sum(y)/len(y), len(y)*0.5*(max(y)-min(y))/sum(y), 0.38, 0]
    if len(y) < 4:
        return startpar, perr, 'not enough data points for a fit, guessing'
    def model_sin(x, avg, contrast, freq, phase):
        return avg + avg * contrast * np.sin(freq * x + phase)
    try:
        popt = startpar
        popt, pcov = curve_fit(model_sin, x, y, startpar, np.sqrt(np.abs(y)))
        perr = np.sqrt(abs(np.diagonal(pcov)))
        return popt, perr, ''
    except Exception as e:
        return popt, perr, 'Error during fit: %s' % e


class CascadeDetector(MiraCascadeDetector):
    """Reseda version of the CascadeDetector

    adds fitting a sin to the timechannels in tof mode"""

    def doReadArray(self, quality):
        data = super(CascadeDetector, self).doReadArray(quality)
        if self.mode != 'tof':
            return data
        # need to append our stuff to self.readresult
        # minor race condition here (and double cache updates!)
        # XXX: needs rewrite/refactor of MiraCascadeDetector

        # demux timing into foil + timing
        shaped = data.reshape(8,16,128,128) # foil, time, x, y
        # note: we have to skip foils 3+4 (not fitted yet)
        x = []
        y = []
        perfoil = 6*[[]]
        # 'time' ranges from 0..15
        for t in range(16):
            _sum = 0
            for foil in [5]:  # ???? should be [0,1,2,5,6,7] !
                # XXX: roi evaluation?
                tf = np.sum(shaped[foil][t])
                _sum += tf
            x.append(t)
            y.append(_sum)
            for foil in range(6):
                tf = np.sum(shaped[foil if foil < 3 else foil + 2][t])
                perfoil[foil].append(tf)
        # ofs, ampl, freq, phase
        self.log.debug('fitting %r on %r' % (y, x))
        popt, perr, msg = fit_a_sin(x, y)
        self.log.debug('result is %r +/- %r for [avg, contrast, freq, phase]' % (popt, perr))
        if msg:
            self.log.warning(msg)
        self.readresult = list(self.readresult) + [abs(popt[1]), perr[1], popt[0], perr[0]]
        if not msg:
            # also fit per foil data and pack everything together to be send via cache for display
            p = []
            for foil in range(6):
                popt, perr, msg = fit_a_sin(x, perfoil[foil])
                p.append(list([popt[0], perr[0], popt[1], perr[1], popt[2], perr[2], popt[3], perr[3]] + perfoil[foil]))
            self._cache.put(self.name, '_foildata', p, flag='#')
        return data

    def valueInfo(self):
        res = super(CascadeDetector, self).valueInfo()
        if self.mode == 'tof':
            res = res + (Value('fit.contrast', unit='', type='other', errors='next', fmtstr='%.3f'),
                         Value('fit.contrastErr', unit='', type='error', errors='none', fmtstr='%.3f'),
                         Value('fit.avg', unit='', type='other', errors='next', fmtstr='%.1f'),
                         Value('fit.avgErr', unit='', type='error', errors='none', fmtstr='%.1f'))
        return res


class ScanningDetector(NicosScanDet):
    """Reseda scanning detector."""

    parameter_overrides = {
        'positions' : Override(settable=True),
    }

    def _processDataset(self, dataset):
        for det in dataset.detectors:
            for imgdet in det._attached_images:
                if getattr(imgdet, 'mode', None) == 'image':
                    # extract roi.counts
                    roivalues = []
                    scanvalues = []
                    for subset in dataset.subsets:
                        for i,val in enumerate(subset.detvalueinfo):
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
                for i,val in enumerate(subset.detvalueinfo):
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

    def valueInfo(self):
        res = []
        for imgdet in self._attached_detector._attached_images:
            if getattr(imgdet, 'mode', None) in ['image']:
                return (Value('fit.contrast', unit='', type='other', errors='next', fmtstr='%.3f'),
                        Value('fit.contrastErr', unit='', type='error', errors='none', fmtstr='%.3f'),
                        Value('fit.avg', unit='', type='other', errors='next', fmtstr='%.1f'),
                        Value('fit.avgErr', unit='', type='error', errors='none', fmtstr='%.1f'))
        res = []
        for ctr in self._attached_detector._attached_counters:
            res.append(Value('%s.fit.contrast' % ctr.name, unit=ctr.unit, type='other', errors='next', fmtstr='%.3f'))
            res.append(Value('%s.fit.contrastErr' % ctr.name, unit=ctr.unit, type='error', errors='none', fmtstr='%.3f'))
            res.append(Value('%s.fit.avg' % ctr.name, unit=ctr.unit, type='other', errors='next', fmtstr='%.1f'))
            res.append(Value('%s.fit.avgErr' % ctr.name, unit=ctr.unit, type='error', errors='none', fmtstr='%.1f'))
        return tuple(res)

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
#   Jens Krüger <jens.krüger@frm2.tum.de>
#
# *****************************************************************************
"""Utilities for RESEDA instrument."""

from math import pi

import numpy as np

from nicos.utils.fitting import PredefinedFit


class MiezeFit(PredefinedFit):
    """Fits with a sine with given frequency including offset."""

    names = ['mieze']
    fit_title = 'mieze fit'
    fit_params = ['avg', 'contrast', 'phase']
    fit_p_descr = fit_params

    timechannels = 16

    def __init__(self, parstart=None, xmin=None, xmax=None):
        PredefinedFit.__init__(self, parstart, xmin, xmax)
        self.freq = 2 * pi / self.timechannels

    def fit_model(self, x, avg, contrast, phase):
        return avg * (1 + abs(contrast) * np.sin(self.freq * x + phase))

    def guesspar(self, x, y):
        self.freq = 2 * pi / len(y)
        if len(y) == 1:
            contrast = 0
        else:
            contrast = 0.5 * np.ptp(y) * len(y) / (sum(y) + 1e-6)
        yavg = np.average(y)
        return [yavg, contrast, 0]

    def process_result(self, res):
        res.label_x = res.phase
        res.label_y = min(res.curve_x)
        res.freq = self.freq
        res.dfreq = 0
        res.contrast = abs(res.contrast)
        res.label_contents = [
            ('Average', res.avg, res.davg),
            ('Freq', res.freq, res.dfreq),
            ('Contrast', res.contrast, res.dcontrast),
            ('Phase', res.phase, res.dphase),
        ]

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
#   bjoern.pedersen@frm2.tum.de
#
# *****************************************************************************

"""
Tests for the fit functions

General test plan:

Generate data with and without noise and check the fit results
"""

import pytest
import numpy as np

from nicos.utils.fitting import LinearFit, GaussFit, SigmoidFit, TcFit, \
    PolyFit, PearsonVIIFit, PseudoVoigtFit, CosineFit, ExponentialFit


@pytest.fixture(scope='function')
def fitconf(request):
    fitclass = request.param[0]
    fitparams = request.param[1]
    addargs = request.param[2] or {}
    fitter = fitclass(**addargs)
    xdata = np.linspace(1, 10)
    ydata = fitter.fit_model(xdata, **fitparams)
    return fitter, xdata, ydata, fitparams


def idfn(val):
    idstr = val[0].__name__ + ': '
    idstr += str(val[1])
    idstr += ' add. pars: ' + str(val[2]) if val[2] else ''
    return idstr


@pytest.mark.parametrize('fitconf', [
    (LinearFit, {'m': 1, 't': 0}, None),
    (LinearFit, {'m': 2, 't': 1}, None),
    (LinearFit, {'m': -2, 't': 1}, None),
    (LinearFit, {'m': 2, 't': -1}, None),
    (PolyFit, {'a0': 1, 'a1': 0}, {'n': 1}),
    (PolyFit, {'a0': 1, 'a1': 2}, {'n': 1}),
    (PolyFit, {'a0': 1, 'a1': 2, 'a2': 2}, {'n': 2}),
    (PolyFit, {'a0': 1, 'a1': 2, 'a2': 0.5, 'a3': 3}, {'n': 3}),
    (GaussFit, {'x0': 2, 'A': 1, 'fwhm': 0.4, 'B': 0}, None),
    (SigmoidFit, {'a': 1, 'b': 20, 'x0': 4, 'c': 0.5}, None),
    (SigmoidFit, {'a': 10, 'b': -2, 'x0': 4, 'c': 0.5}, None),
    (TcFit, {'B': 2, 'A': 15, 'Tc': 3, 'alpha': .3}, None),
    (TcFit, {'B': 2, 'A': 15, 'Tc': 3, 'alpha': 1.3}, None),
    (PearsonVIIFit, {'B': 1., 'A': 10., 'x0': 3., 'hwhm': 0.5, 'm': 3.}, None),
    (PseudoVoigtFit, {'B': 1., 'A': 20., 'x0': 4., 'hwhm': .3, 'eta': .3}, None),
    (CosineFit, {'A': 20, 'f': .5, 'x0': 2, 'B': .5}, None),
    (ExponentialFit, {'b': -0.3, 'x0': 5}, None),
    ], indirect=['fitconf'], ids=idfn)
def test_fit(fitconf):
    fitter = fitconf[0]
    xdata = fitconf[1]
    ydata = fitconf[2]
    res = fitter.run(xdata, ydata, None)
    assert not res._failed
    for k, v in fitconf[3].items():
        assert getattr(res, k) == pytest.approx(v, rel=1e-6, abs=1e-6)

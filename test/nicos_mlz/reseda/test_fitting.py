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

"""
Tests for the fit functions

Generate data with and without noise and check the fit results
"""

import numpy as np
import pytest

from nicos_mlz.reseda.utils import MiezeFit

from test.utils import approx


@pytest.fixture(scope='function')
def fitconf(request):
    fitclass = request.param[0]
    fitparams = request.param[1]
    addargs = request.param[2] or {}
    fitter = fitclass(**addargs)
    xdata = np.linspace(0, 1, 16)
    ydata = fitter.fit_model(xdata, **fitparams)
    return fitter, xdata, ydata, fitparams


def idfn(val):
    idstr = val[0].__name__ + ': '
    idstr += str(val[1])
    idstr += ' add. pars: ' + str(val[2]) if val[2] else ''
    return idstr


class TestMiezeFit:

    @pytest.mark.parametrize('fitconf', [
        (MiezeFit, {'avg': 1, 'phase': 0, 'contrast': 1}, None),
        ], indirect=['fitconf'], ids=idfn)
    def test_fit(self, fitconf):
        fitter = fitconf[0]
        xdata = fitconf[1]
        ydata = fitconf[2]
        res = fitter.run(xdata, ydata, None)
        assert not res._failed
        for k, v in fitconf[3].items():
            assert getattr(res, k) == approx(v, rel=1e-6, abs=1e-6)

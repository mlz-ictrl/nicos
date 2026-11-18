# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS tests for nicos.commands.analyze."""

import pytest

from nicos.commands.analyze import ListFitters, center_of_mass, fit, fwhm, \
    gauss, lorentz, pearson, poly, root_mean_square, voigt
from nicos.core import FINAL

try:
    from scipy.optimize import leastsq
except ImportError:
    leastsq = None


session_setup = 'scanning'


@pytest.fixture(scope='class', autouse=True)
def generate_dataset(session):
    """Generate a dataset as if a scan has been run."""
    import numpy
    data = numpy.array((1, 2, 1, 2, 2, 2, 5, 20, 30, 20, 10, 2, 3, 1, 2, 1, 1, 1))
    xpoints = numpy.arange(-9, 9)
    assert len(data) == len(xpoints)
    tdev = session.getDevice('tdev')
    det = session.getDevice('det')
    dataman = session.experiment.data
    dataman.beginScan(devices=[tdev], detectors=[det])
    for (x, y) in zip(xpoints, data):
        dataman.beginPoint()
        dataman.putValues({'tdev': (None, x)})
        dataman.putResults(FINAL, {'det': ([0, 0, y, y*2], [])})
        dataman.finishPoint()
    dataman.finishScan()


class TestAnalyzers:

    def test_fwhm(self, session):
        result = fwhm(1, 3)
        assert result == (2.75, -1, 30, 1)

    def test_center_of_mass(self, session, log):
        result1 = center_of_mass()
        assert result1 == pytest.approx(-0.8395, abs=0.0005)
        result2 = center_of_mass(4)  # center of mass from values*2 should be same
        assert result1 == result2

        with log.assert_msg_matches([
            r'parameter       value     error  rel. error',
            r'==============  ========  =====  ==========',
            r'Center of mass  -0.83962  \+/- 0  \+/- 0.0%',
            ]):
            result = fit('center_of_mass')
        assert len(result) == 2
        assert len(result[0]) == 1
        assert result[0][0] == pytest.approx(-0.83962, abs=0.00001)

    def test_root_mean_square(self, session):
        result = root_mean_square()
        assert 10.176 < result < 10.177

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_poly(self, session):
        result1 = poly(1, 1, 3)
        assert len(result1) == 2
        assert len(result1[0]) == 2
        assert 1.847 < result1[0][0] < 1.848
        result2 = poly(2)
        assert -0.047 < result2[0][2] < -0.046
        result3 = poly(2, 4)
        assert -0.094 < result3[0][2] < -0.093
        result4 = poly(2, 1, 4)
        assert result4 == result3

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_gauss(self, session, log):
        msgs = [
            r'parameter   value     error         rel. error',
            r'==========  ========  ============  ==========',
            r'center      -0.87383  \+/- 0.069174  \+/- 7.9%',
            r'amplitude   28.267    \+/- 2.0151    \+/- 7.1%',
            r'FWHM        2.6351    \+/- 0.13556   \+/- 5.1%',
            r'background  1.2998    \+/- 0.16555   \+/- 12.7%',
        ]
        with log.assert_msg_matches(msgs):
            result = gauss()
        assert len(result) == 2
        assert len(result[0]) == 4
        assert result[0][0] == pytest.approx(-0.8735, abs=0.0005)
        assert result[0][1] == pytest.approx(28.267, abs=0.0005)
        assert result[0][2] == pytest.approx(2.6351, abs=0.0005)
        assert result[0][3] == pytest.approx(1.2998, abs=0.0005)

        with log.assert_msg_matches(msgs):
            result1 = fit('gauss')
        assert result == result1

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_lorentz(self, session, log):
        msgs = [
            r'parameter   value     error        rel. error',
            r'==========  ========  ===========  ==========',
            r'center      -0.88226  \+/- 0.1103   \+/- 12.5%',
            r'amplitude   32.372    \+/- 3.755    \+/- 11.6%',
            r'FWHM        1.9455    \+/- 0.24488  \+/- 12.6%',
            r'background  0.37567   \+/- 0.31561  \+/- 84.0%',
        ]
        with log.assert_msg_matches(msgs):
            result = lorentz()
        assert len(result) == 2
        assert len(result[0]) == 4
        assert result[0][0] == pytest.approx(-0.882, abs=0.001)

        with log.assert_msg_matches(msgs):
            result1 = fit('lorentz')
        assert result == result1

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_voigt(self, session, log):
        msgs = [
            r'parameter   value     error         rel. error',
            r'==========  ========  ============  ==========',
            r'background  1.0312    \+/- 0.29389   \+/- 28.5%',
            r'amplitude   29.35     \+/- 2.3687    \+/- 8.1%',
            r'center      -0.88388  \+/- 0.069641  \+/- 7.9%',
            r'HWHM        1.2644    \+/- 0.093241  \+/- 7.4%',
            r'eta         0.19805   \+/- 0.18698   \+/- 94.4%',
        ]
        with log.assert_msg_matches(msgs):
            result = voigt()
        assert len(result) == 2
        assert len(result[0]) == 5
        assert result[0][2] == pytest.approx(-0.883, abs=0.001)

        with log.assert_msg_matches(msgs):
            result1 = fit('pseudovoigt')
        assert result == result1

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_pearson(self, session, log):
        msgs = [
            r'parameter   value     error         rel. error',
            r'==========  ========  ============  ==========',
            r'background  1.2915    \+/- 0.17981   \+/- 13.9%',
            r'amplitude   28.415    \+/- 2.447[ 1]    \+/- 8.6%',
            r'center      -0.87607  \+/- 0.071994  \+/- 8.2%',
            r'HWHM        1.3057    \+/- 0.11813   \+/- 9.0%',
            r'm           35.9[7-9][ 0-9]    \+/- 251.[5-7][0-9]    \+/- 699.[1-3]%',
        ]
        with log.assert_msg_matches(msgs):
            result = pearson()
        assert len(result) == 2
        assert len(result[0]) == 5
        assert result[0][2] == pytest.approx(-0.876, abs=0.001)

        with log.assert_msg_matches(msgs):
            result1 = fit('pearson')
        assert result == result1

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_tc(self, session):
        result = fit('tc')
        assert len(result) == 2
        # assert result == (None, None)  # Not expected to fit!


def test_list_fitters(session, log):
    with log.assert_msg_matches([
        r'name            can center',
        r'==============  ==========',
        r'center_of_mass  yes',
        r'cos             yes',
        r'cosine          yes',
        r'exp             no',
        r'exponential     no',
        r'gauss           yes',
        r'gaussian        yes',
        r'line            no',
        r'linear          no',
        r'lorentz         yes',
        r'lorentzian      yes',
        r'pearson         yes',
        r'pearson-vii     yes',
        r'pseudo-voigt    yes',
        r'pseudovoigt     yes',
        r'sigmoid         yes',
        r'tc              yes',
        r'tcfit           yes',
        ]):
        ListFitters()

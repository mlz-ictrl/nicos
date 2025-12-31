# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

from random import randint

import pytest

pytest.importorskip('uncertainties', reason='Uncertainties module is missing')

from nicos_jcns.moke01.utils import calculate, generate_intvb

try:
    import tango
except ModuleNotFoundError:
    tango = None

from nicos.utils.functioncurves import AffineScalarFunc, Curve2D, \
    CurvePoint2D, Curves

session_setup = 'moke01'


@pytest.mark.skipif(tango is None, reason='pytango module is missing')
def test_basic(session):
    magb = session.getDevice('MagB')
    ps = session.getDevice('PS_current')
    ps.doStart(300)
    assert ps.read(0) == 300
    b0 = magb.read(0)
    assert b0 == 750
    ps.doStart(1000)
    ps.doStart(300)
    b1 = magb.read(0)
    assert b1 > b0


@pytest.mark.skipif(tango is None, reason='pytango module is missing')
def test_cycle_currentsource(session):
    magb = session.getDevice('MagB')
    Imin, Imax, n = randint(-1000, -100), randint(100, 1000), randint(1, 5)
    # ramp is set to 1 A/min for simplicity
    magb.cycle_currentsource(float(Imin), float(Imax), 1, n)
    magb.disable()
    dIs = [abs(Ivt.y.n - magb._Ivt[i - 1].y.n) for i, Ivt in enumerate(magb._Ivt) if i]
    dI = sum(dIs) / len(dIs)
    for di in dIs:
        assert pytest.approx(di) == pytest.approx(dI)
    assert len(magb._Ivt) == 2 * n * 100
    assert magb._cycling_steps == [100] * 2 * n


@pytest.mark.skipif(tango is None, reason='pytango module is missing')
def test_magnet(session):
    magb = session.getDevice('MagB')
    magb.ramp = 1e4
    # kinda y = x - 400
    magb.prevtarget = -1000
    assert magb._current2field(-250).n == -750
    assert magb._field2current(750).n == 300
    # kinda y = x + 400
    magb.prevtarget = 1000
    assert magb._current2field(250).n == 750
    assert magb._field2current(-750).n == -300
    # test calibration factor
    calfac = magb.calfac.copy()
    calfac['stepwise'] = 0.1
    magb.calfac = calfac
    assert magb._current2field(250).n == 75
    assert magb._field2current(-75).n == -300


@pytest.mark.skipif(tango is None, reason='pytango module is missing')
def test_calibration(session):
    magb = session.getDevice('MagB')
    ramp = 0
    rampstr = format(ramp, '.1f')
    n = 1
    # test only stepwise mode
    mode = 'stepwise'
    magb.calibrate(mode, ramp, n)
    calcurves = magb.calibration[mode][rampstr]
    assert mode in magb.calibration.keys()
    # calibrations should result in two curves: increasing and decreasing
    assert isinstance(calcurves, Curves)
    assert isinstance(calcurves.increasing(), Curves)
    assert isinstance(calcurves.decreasing(), Curves)
    assert len(calcurves) == 2
    for i in range(2):
        assert isinstance(calcurves[i], Curve2D)
        assert isinstance(calcurves[i][0], CurvePoint2D)
        assert isinstance(calcurves[i][0].x, AffineScalarFunc)
        assert isinstance(calcurves[i][0].x.n, float)
        assert isinstance(calcurves[i][0].x.s, float)
        assert isinstance(calcurves[i][0].y, AffineScalarFunc)
        assert isinstance(calcurves[i][0].y.n, float)
        assert isinstance(calcurves[i][0].y.s, float)
    # new calibrations should have the same curve as the one from setup
    for curve0, curve1 in zip(magb.calibration[mode]['10000.0'], calcurves):
        for BvI in curve1:
            assert pytest.approx(BvI.y.n) == pytest.approx(curve0.yvx(BvI.x).y.n)


@pytest.mark.skipif(tango is None, reason='pytango module is missing')
def test_intensity_measurement(session):
    mrmnt = {'Bmin': -500.0, 'Bmax': 500.0, 'ramp': 0.0, 'cycles': 1,
             'step': 50.0, 'steptime': 0, 'mode': 'stepwise',
             'exp_type': 'ell', 'field_orientation': 'polar', 'id': 'test'}
    magb = session.getDevice('MagB')
    magb.calibrate('stepwise', 0, 1)
    magb.ramp = 0
    magb.userlimits = magb.abslimits
    magb.measure_intensity(mrmnt)
    IntvB = magb.measurement['IntvB']
    assert isinstance(IntvB, Curve2D)
    # Virtual Intensity device generates _/‾ -shaped curve with some random
    # features for B values from -1000 mT to 1000 mT
    # it is hardcoded that min/max intensity levels are 1 and 2 V
    assert IntvB.xmin.n == -500
    assert IntvB.xmax.n == 500
    assert IntvB.ymin.n <= 1600
    assert IntvB.ymax.n >= 1700
    assert 1600 < IntvB.series_to_curves().mean().yvx(0).y < 1700


def test_kerr_calc():
    # IntvB curve can be modelled as two error function curves,
    # the input for the curves is randomized
    temp = generate_intvb(-1000, 1000)
    IntvB = Curve2D(temp[0])
    IntvB.append(temp[1])
    # angle and extinction values are of the typical range, randomized
    int_mean = IntvB.series_to_curves().mean().yvx(0).y
    angle = randint(100, 250) / 10
    extinction = randint(10, 90) / 100
    fit_min, fit_max, IntvB, EvB, kerr = calculate(IntvB, int_mean, angle, extinction)
    # erfcs are designed to have min and max Y values at 1 and 2
    assert fit_min[0] is not None
    assert pytest.approx(fit_min[1].n, rel=0.05) == 1600
    assert fit_max[0] is not None
    assert pytest.approx(fit_max[1].n, rel=0.05) == 1700
    # IntvB that is in the output differs from the input,
    # input allows multiple curves, and the output is a mean curve
    assert isinstance(IntvB, Curve2D)
    assert IntvB
    assert len(EvB.series_to_curves()) == 2
    assert EvB[0].y < EvB[int(len(EvB) / 2)].y > EvB[-1].y
    # kerr angle must be a positive value
    assert kerr > 0

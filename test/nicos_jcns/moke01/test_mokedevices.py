# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

import numpy
import pytest
import scipy

# pylint: disable=import-error
try:
    import uncertainties
    from nicos_jcns.moke01.utils import calculate
except ModuleNotFoundError:
    uncertainties = None

try:
    import tango
except ModuleNotFoundError:
    tango = None

from nicos.utils.functioncurves import AffineScalarFunc, Curve2D, \
    CurvePoint2D, Curves


session_setup = 'moke01'


@pytest.mark.skipif(uncertainties is None,
                    reason='Uncertainties module is missing')
@pytest.mark.skipif(tango is None,
                    reason='pytango module is missing')
def test_basic(session):
    magb = session.getDevice('MagB')
    intensity = session.getDevice('Intensity')
    magsensor = session.getDevice('Mag_sensor')
    ps = session.getDevice('PS_current')
    assert magb.read() == 0.0
    assert intensity.read() == 1.0
    assert magsensor.read() == 0.0
    ps.doStart(1)
    assert ps.read() == 1.0
    ps.doStart(0)


@pytest.mark.skipif(uncertainties is None,
                    reason='Uncertainties module is missing')
@pytest.mark.skipif(tango is None,
                    reason='pytango module is missing')
def test_cycle_currentsource(session):
    magb = session.getDevice('MagB')
    v1, v2, n = randint(-400, -1), randint(1, 400), randint(1, 5)
    # ramp is set to 1 A/min for simplicity
    magb.cycle_currentsource(float(v1), float(v2), 1, n)
    magb.disable()
    dIs = [v.y.n - magb._Ivt[i - 1].y.n for i, v in enumerate(magb._Ivt) if i]
    for dI in dIs:
        assert pytest.approx(abs(dI)) == pytest.approx((v2 - v1) / 100)
    assert len(magb._Ivt) == 2 * n * 100
    assert magb._cycling_steps == [100] * 2 * n


@pytest.mark.skipif(uncertainties is None,
                    reason='Uncertainties module is missing')
@pytest.mark.skipif(tango is None,
                    reason='pytango module is missing')
def test_magnet(session):
    ramp = 400 # A/min
    magb = session.getDevice('MagB')
    temp = magb.calibration.copy()
    temp['stepwise'][str(float(ramp))] = Curves([[(-400, -800), (400, 0)],
                                                 [(400, 800), (-400, 0)]])
    magb.calibration = temp
    # kinda y = x - 400
    magb.prevtarget = -800
    assert magb._current2field(100).n == -300.0
    assert magb._field2current(-300).n == 100
    # kinda y = x + 400
    magb.prevtarget = 800
    assert magb._current2field(-100).n == 300.0
    assert magb._field2current(300).n == -100
    # test calibration factor
    calfac = magb.calfac.copy()
    calfac['stepwise'] = 0.1
    magb.calfac = calfac
    assert magb._current2field(-100).n == 30.0
    assert magb._field2current(30).n == -100


@pytest.mark.skipif(uncertainties is None,
                    reason='Uncertainties module is missing')
@pytest.mark.skipif(tango is None,
                    reason='pytango module is missing')
def test_calibration(session):
    magb = session.getDevice('MagB')
    magsensor = session.getDevice('Mag_sensor')
    magsensor.testqueue = (list(range(400, -400, -8)) +
                           list(range(-400, 400, 8))) * 2
    magsensor.simulate = True
    ramp = 400
    n = 1
    magb.calibrate('stepwise', ramp, n)
    magb.enable()
    magb.calibrate('continuous', ramp, n)
    assert 'stepwise' in magb.calibration.keys()
    assert 'continuous' in magb.calibration.keys()
    ramp = str(float(ramp))
    for curve in magb.calibration['stepwise']['400.0']:
        assert curve.x == curve.y
    # due to interpolation of Ivt and Bvt curves it is not clear which values
    # will be, so we need to be sure there are 2 curves and types are ok
    assert len(magb.calibration['continuous'][ramp]) == 2
    for mode in ['stepwise', 'continuous']:
        assert isinstance(magb.calibration[mode][ramp], Curves)
        assert isinstance(magb.calibration[mode][ramp].increasing(), Curves)
        assert isinstance(magb.calibration[mode][ramp].decreasing(), Curves)
        for i in range(2):
            assert isinstance(magb.calibration[mode][ramp][i], Curve2D)
            assert isinstance(magb.calibration[mode][ramp][i][0], CurvePoint2D)
            assert isinstance(magb.calibration[mode][ramp][i][0].x,
                              AffineScalarFunc)
            assert isinstance(magb.calibration[mode][ramp][i][0].x.n, float)
            assert isinstance(magb.calibration[mode][ramp][i][0].x.s, float)
            assert isinstance(magb.calibration[mode][ramp][i][0].y,
                              AffineScalarFunc)
            assert isinstance(magb.calibration[mode][ramp][i][0].y.n, float)
            assert isinstance(magb.calibration[mode][ramp][i][0].y.s, float)


@pytest.mark.skipif(uncertainties is None,
                    reason='Uncertainties module is missing')
@pytest.mark.skipif(tango is None,
                    reason='pytango module is missing')
def test_intensity_measurement(session):
    magsensor = session.getDevice('Mag_sensor')
    # there are two extra read() before and after `measure_intensity`
    magsensor.testqueue = [1,] + list(range(400, -400, -40)) + \
                          list(range(-400, 400, 40)) + [400, 2, 3]
    magsensor.simulate = True
    mrmnt = {'Bmin': -400.0, 'Bmax': 400.0, 'ramp': 400.0, 'cycles': 1,
             'step': 40.0, 'steptime': 1, 'mode': 'stepwise',
             'exp_type': 'ell', 'field_orientation': 'polar', 'id': 'test'}
    magb = session.getDevice('MagB')
    temp = magb.calibration.copy()
    temp[mrmnt['mode']][str(mrmnt['ramp'])] = \
        Curves([[(-400, -400), (400, 400)], [(400, 400), (-400, -400)]])
    magb.calibration = temp
    magb.userlimits = (-400, 400)
    magb.measure_intensity(mrmnt)
    assert magb.measurement['BvI'].x == magb.measurement['BvI'].y
    assert magb.measurement['BvI'].x == magb.measurement['IntvB'].x
    for p in magb.measurement['IntvB']:
        assert p.y == 1.0


@pytest.mark.skipif(uncertainties is None,
                    reason='Uncertainties module is missing')
def test_kerr_calc():
    # IntvB curve can be modelled as two error function curves,
    # the input for the curves is randomized
    B = randint(20, 90)
    Bmin = - B / 100
    Bmax = - Bmin
    width = randint(3, 15)
    x = numpy.linspace(Bmin, Bmax, 100, True)
    y1 = scipy.special.erf(x * 200 + width) / 2 + 1.5
    y1 = [uncertainties.ufloat(y, randint(1, 10) / 100) for y in y1]
    y2 = scipy.special.erf(x * 200 - width) / 2 + 1.5
    y2 = [uncertainties.ufloat(y, randint(1, 10) / 100) for y in y2]
    IntvB = Curve2D.from_x_y(x, y1)
    IntvB.append(Curve2D.from_x_y(x[::-1], y2[::-1]))
    # angle and extinction values are of the typical range, randomized
    int_mean = IntvB.series_to_curves().mean().yvx(0).y
    angle = randint(100, 250) / 10
    extinction = randint(10, 90) / 100
    fit_min, fit_max, IntvB, EvB, kerr = calculate(IntvB, int_mean, angle, extinction)
    # erfcs are designed to have min and max Y values at 1 and 2
    assert fit_min[0] is not None and \
           pytest.approx(fit_min[1].n, abs=0.1) == 1.0
    assert fit_max[0] is not None and \
           pytest.approx(fit_max[1].n, abs=0.1) == 2.0
    # IntvB that is in the output differs from the input,
    # input allows multiple curves, and the output is a mean curve
    assert isinstance(IntvB, Curve2D) and IntvB
    assert len(EvB.series_to_curves()) == 2
    assert EvB[0].y < EvB[int(len(EvB) / 2)].y > EvB[-1].y
    # kerr angle must be a positive value
    assert kerr > 0

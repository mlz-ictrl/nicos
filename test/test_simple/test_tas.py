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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from math import radians

import pytest
from numpy import allclose, array, dot, sqrt
from pytest import approx

from nicos.commands.measure import count
from nicos.commands.tas import Q, _resmat_args, acc_bragg, alu, calpos, \
    checkalign, copper, ho_spurions, pos, qcscan, qscan, rescal, rp, \
    setalign
from nicos.core import ComputationError, ConfigurationError, \
    InvalidValueError, LimitError, MoveError, PositionError, UsageError, \
    status
from nicos.devices.sxtal.goniometer.posutils import Xrot, Yrot, Zrot

from test.utils import ErrorLogged

session_setup = 'tas'


@pytest.fixture(scope='function')
def tas(session):
    """Create a common set up at the start of the TAS test."""

    tasdev = session.getDevice('Tas')
    tasdev.scanmode = 'CKF'
    tasdev.scanconstant = 2.662
    tasdev.scatteringsense = (1, -1, 1)
    tasdev.energytransferunit = 'THz'
    tasdev._attached_mono.unit = 'A-1'
    tasdev._attached_ana.unit = 'A-1'
    sample = session.getDevice('Sample')
    sample.lattice = [2.77, 2.77, 2.77]
    sample.angles = [90, 90, 90]
    sample.orient1 = [1, 0, 0]
    sample.orient2 = [0, 1, 1]
    sample.psi0 = 0
    return tasdev


def assertPos(pos1, pos2):
    for v1, v2 in zip(pos1, pos2):
        assert v1 == approx(v2, abs=1e-3)


def test_mono_device(session):
    mono = session.getDevice('t_mono')
    mth = session.getDevice('t_mth')
    # unit switching
    mono.unit = 'A-1'
    mono.maw(1.4)
    assert mono.read(0) == approx(1.4, abs=1e-3)
    assert mono.target == 1.4
    mono.unit = 'meV'
    assert mono.read(0) == approx(4.061, abs=1e-3)
    assert mono.target == approx(4.061, abs=1e-3)
    assert mono.status()[0] == status.OK

    for unit in ['THz', 'A', 'A-1']:
        mono.unit = unit
        assert mono.status()[0] == status.OK

    # mth/mtt mismatch
    mth.maw(mth() + 5)
    assert mono.status(0)[0] == status.NOTREACHED

    old = mono.read(0)

    mono.reset()
    pytest.raises(LimitError, mono.doStart, 0.11)
    pytest.raises(LimitError, mono.maw, 0.11)

    mono.maw(1.5)

    for mode in ['flat', 'vertical', 'double', 'manual']:
        mono.focmode = mode
        mono.maw(1.5)

    mono.maw(old)

    mono.hfocuspars = mono.hfocuspars
    mono.vfocuspars = mono.vfocuspars

    mtt = session.getDevice('t_mtt')
    mtt.move(mtt.read(0) + 2)
    mono.finish()

    assert mono._calcurvature(1., 1., 1) == approx(1.068, abs=1e-3)


def test_tas_mono_foci(session, tas):
    mono = session.getDevice('t_mono')
    mono._setROParam('target', None)
    val = mono.read(0)
    for mode in ['flat', 'vertical', 'double', 'manual']:
        mono.focmode = mode
        mono.wait()
        assert mono.read(0) == val


def test_tas_device(session, tas):
    mono = session.getDevice('t_mono')
    ana = session.getDevice('t_ana')
    phi = session.getDevice('t_phi')
    psi = session.getDevice('t_psi')
    ki = session.getDevice('t_ki')
    kf = session.getDevice('t_kf')

    # test the correct driving of motors
    tas.maw([1, 0, 0, 1])
    assert ana() == approx(2.662, abs=1e-3)
    assert mono() == approx(3.014, abs=1e-3)
    assert phi() == approx(-46.6, abs=0.1)
    assert psi() == approx(105.1, abs=0.1)
    assertPos(tas(), [1, 0, 0, 1])

    # cannot go to position out of scattering triangle
    pytest.raises(LimitError, tas, [5, 0, 0, 0])
    # cannot go to position out of scattering plane
    pytest.raises(LimitError, tas, [1, 2, 1, 0])
    # cannot go beyond motor limits
    old_limits = psi.userlimits
    psi.userlimits = (0, 50)
    pytest.raises(LimitError, tas, [1, 0, 0, 1])
    psi.userlimits = old_limits

    # test scattering sense
    tas.scatteringsense = [-1, 1, -1]
    tas.maw([1, 0, 0, 1])
    assert phi() == approx(46.6, abs=0.1)  # now with "+" sign
    pytest.raises(ConfigurationError, setattr, tas, 'scatteringsense',
                  [2, 0, 2])

    # test energytransferunit
    mono(1)
    ana(2)
    tas.energytransferunit = 'meV'
    assert tas()[3] == approx(-6.216, abs=1e-3)
    tas.energytransferunit = 'THz'
    assert tas()[3] == approx(-1.503, abs=1e-3)
    pytest.raises(InvalidValueError, setattr, tas, 'energytransferunit',
                  'A-1')

    # test scanmode
    tas.scanmode = 'CKI'
    tas.scanconstant = 2.662
    tas.maw([1, 0, 0, 1])
    assert mono() == approx(2.662, abs=1e-3)
    tas.scanmode = 'CKF'
    tas.maw([1, 0, 0, 1])
    assert ana() == approx(2.662, abs=1e-3)
    tas.scanmode = 'DIFF'
    tas.scanconstant = 2.5
    ana(2.5)
    tas.maw([1, 0, 0, 0])
    assert ana() == approx(2.5, abs=1e-3)
    assert mono() == approx(2.5, abs=1e-3)
    assertPos(tas(), [1, 0, 0, 0])
    # XXX shouldn't this result in an error?
    # pytest.raises(tas, [1, 0, 0, 1])
    pytest.raises(ConfigurationError, setattr, tas, 'scanmode', 'BLAH')

    # test sub-devices and wavevector devices
    kf(2.662)
    tas.maw([1, 0, 0, 1])
    assert ki.read(0) == approx(3.014, abs=1e-3)
    assert kf.read(0) == approx(2.662, abs=1e-3)
    assert tas.h() == approx(1, abs=1e-3)
    assert tas.k() == approx(0, abs=1e-3)
    assert tas.l() == approx(0, abs=1e-3)
    assert tas.E() == approx(1, abs=1e-3)
    tas.h.maw(1.5)
    assert tas.h() == approx(1.5, abs=1e-3)


def test_error_handling(session, log, tas):
    # check that if one subdev errors out, we wait for the other subdevs
    mfh = session.getDevice('t_mfh')
    phi = session.getDevice('t_phi')

    tas.maw([1.01, 0, 0, 1])
    phi.speed = 1
    mfh._status_exception = PositionError(mfh, 'wrong position')
    with log.allow_errors():
        try:
            tas.maw([1, 0, 0, 1])
        except MoveError:
            pass
        else:
            pytest.fail('PositionError not raised')
        # but we still arrived with phi
        assert phi() == approx(-46.6, abs=0.1)


def test_qscan(session, tas):
    sgx = session.getDevice('sgx')
    qscan((1, 0, 0), Q(0, 0, 0, 0.1), 5, sgx, 'scaninfo', t=1)
    qscan((0, 0, 0), (0, 0, 0), 5, 2.5, t_kf=2.662, manual=1,
          h=1, k=1, l=1, e=0, dH=0, dk=0, dl=0, dE=.1)
    qcscan((1, 0, 0), Q(0, 0, 0, 0.1), 3, manual=[1, 2])
    qscan((1, 0, 0), Q(0, 0, 0, 0), 1)
    qscan((1, 0, 0, 0), Q(0, 0, 0, 0), 1)
    qscan([1, 0, 0, 0], [0, 0, 0, 0], 1)
    qscan([1, 0, 0, 0], (0, 0, 0, 0), 1)
    qscan(array((1, 0, 0, 0)), array([0, 0, 0, 0]), 1)

    qscan((1, 0, 0, '2'), [0, 0, '0.2', 0], 1)
    qscan('1000', (0, 0, 0), 1)
    qscan(1, 0.1, 1)
    qscan((i for i in (1, 0, 0)), (0, 0, 0), 1)

    qscan((2, 0, 0, '2'), (0.1, 0, 0, 0), 10, 'x1!', 'x23', t=1, h=3, dE=0.2)
    qscan((2, 0, 0, '2'), (0.1, 0, 0, 0), 10, 'x1!', 'x23', t=1, h=3, dE='0.2')

    pytest.raises(UsageError, qscan, 'abc', (0, 0, 0), 1)
    pytest.raises(UsageError, qscan, (1, 0, 0, 0, 0), (0, 0, 0), 10)
    pytest.raises(UsageError, qscan, (1, 0, 0), (0, 0, 0), 10)
    pytest.raises(UsageError, qcscan, (1, 0, 0), (0, 0, 0), 10)


def test_tas_commands(session, log, tas):
    tas.scanmode = 'CKI'
    tas.scanconstant = 1.57

    # calpos()/pos()
    for args in [
        (0.5, 0.5, 0.5),
        (0.5, 0.5, 0.5, 0),
        (0.5, 0.5, 0.5, 0, 1.57),
        ((0.5, 0.5, 0.5, 0),),
        (Q(0.5, 0.5, 0.5, 0),),
        (Q(0.5, 0.5, 0.5, 0), 1.57)
    ]:
        # move tas to known position
        tas.maw([0.4, 0.4, 0.4, 0.2])
        calpos(*args)
        pos()
        assertPos(tas(), [0.5, 0.5, 0.5, 0])
        # move tas to known position
        tas.maw([0.4, 0.4, 0.4, 0.2])
        pos(*args)
        assertPos(tas(), [0.5, 0.5, 0.5, 0])

    tas.maw([0.4, 0.4, 0.4, 0.2])
    with log.assert_warns('position not allowed'):
        calpos(0.7, 0.7, 0.7, 0)
    calpos(0.5, 0.5, 0.5, 0)
    pytest.raises(ErrorLogged, calpos, 1, 0, 0, 1)
    pos()  # still goes to last successful calpos()
    assertPos(tas(), [0.5, 0.5, 0.5, 0])
    rp()  # just check that it works

    pytest.raises(ComputationError, pos, (1, 2, 3))
    pytest.raises(LimitError, pos, (0.7, 0.7, 0.7))

    pytest.raises(UsageError, calpos, 1, 0, 0, 0, 0, 0)
    pytest.raises(UsageError, pos, 1, 0, 0, 0, 0, 0)


def test_qmodulus(session, log):
    qmod = session.getDevice('Qmod')
    assert qmod.unit == 'A-1'
    assert qmod.status(0) == (status.OK, '')
    assert qmod.read(0) == approx(10.7849, abs=1e-4)


def test_setalign(session, tas):
    pos(.5, .5, .5)
    setalign((-.5, .5, .5))
    assertPos(tas.read(0), [-.5, .5, .5, 0])
    setalign(Q(0.5, 0.5, 0.5, 1))
    assertPos(tas.read(0), [.5, .5, .5, 0])


def test_checkalign(session, tas):
    tas = session.getDevice('Tas')
    tdet = session.getDevice('vtasdet')
    tas.scanmode = 'CKI'
    tas.scanconstant = 1.57
    checkalign((1, 0, 0), 0.05, 2, tdet, accuracy=0.1)
    checkalign(Q(1, 0, 0, 2), 0.05, 2, tdet, accuracy=0.1)


def test_helper_commands(tas):
    # just check that they are working
    acc_bragg(1, 0, 0, 0)
    ho_spurions()
    alu(phi=50)
    copper(phi=50)


def test_resolution(session, tas):
    tas.scanmode = 'CKI'
    tas.maw([1.01, 0, 0, 1])
    cell = tas._attached_cell
    cfg, par = _resmat_args((1, 1, 0, 0), {})
    assert len(cfg) == 30
    assert par['qx'] == 1
    assert par['en'] == 0
    assert par['as'] == cell.lattice[0]
    assert par['alpha1'] == 20
    assert par['alpha4'] == 60
    assert par['beta1'] == 6000

    rescal()
    rescal(1, 1, 0)
    rescal(1, 1, 0, 1)


def test_virtualdet(session, tas):
    tdet = session.getDevice('vtasdet')
    tas.scanmode = 'CKI'
    tas.scanconstant = 1.57
    tas.maw([1, 0, 0, 0])
    countres = count(tdet, 1)
    assert countres[0] == 1.0
    cps = float(countres[2])
    countres2 = count(tdet, 100)
    assert countres2[2] / cps == approx(100, abs=30)

    tas.maw([0.5, 0, 0, 0])
    countres = count(tdet, 1)
    assert countres[2] < 10

    countres = count(tdet, mon=10000)
    assert countres[1] == 10000


def test_virtualgonios(session, tas):
    gx, gy = session.getDevice('sgx'), session.getDevice('sgy')
    v1, v2 = session.getDevice('vg1'), session.getDevice('vg2')

    # when psi0 = 0, gx == v1 and gy == v2
    tas._attached_cell.psi0 = 0
    gx.maw(0)
    gy.maw(0)
    assert v1.read(0) == 0
    assert v2.read(0) == 0
    gx.maw(2)
    assert v1.read(0) == approx(2)
    assert v2.read(0) == approx(0)
    gy.maw(1)
    assert v1.read(0) == approx(2)
    assert v2.read(0) == approx(1)

    v1.maw(0)
    v2.maw(1.3)
    assert gx.read(0) == approx(0)
    assert gy.read(0) == approx(1.3)

    # psi0 = 45deg
    tas._attached_cell.psi0 = 45
    gx.maw(0)
    gy.maw(0)
    assert v1.read(0) == 0
    assert v2.read(0) == 0
    v1.maw(4)
    assert gx.read(0) == approx(2 * sqrt(2), abs=5e-2)
    assert gy.read(0) == approx(2 * sqrt(2), abs=5e-2)

    # limits of sgx, sgy are +/- 5 deg
    v1.maw(7)
    pytest.raises(LimitError, v2.maw, 3)

    # make sure the calculations match intent
    tas._attached_cell.psi0 = 64
    v1.maw(1.5)
    v2.maw(-2)

    # extract angles in radians
    psi = radians(64)
    x1 = radians(1.5)
    y1 = radians(-2)
    x2 = radians(gx.read(0))
    y2 = radians(gy.read(0))

    # these two matrices should deliver the same rotation
    m1 = dot(Xrot(x1), Yrot(y1))
    m2 = dot(dot(Zrot(psi), Xrot(x2)), dot(Yrot(y2), Zrot(-psi)))
    assert allclose(m1, m2, atol=1e-3)

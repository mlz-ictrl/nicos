#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

import pytest

from nicos.core import UsageError, LimitError, ConfigurationError, MoveError, \
    InvalidValueError, ComputationError, PositionError, status
from nicos.commands.tas import qscan, qcscan, Q, calpos, pos, rp, \
    acc_bragg, ho_spurions, alu, copper, rescal, _resmat_args, \
    setalign, checkalign
from nicos.commands.measure import count

from test.utils import raises, approx, ErrorLogged

session_setup = 'tas'


@pytest.fixture
def tas(session):
    # Create a common set up at the start of the test.
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
    assert raises(LimitError, mono.doStart, 0.11)
    assert raises(LimitError, mono.maw, 0.11)

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

    assert mono._calcurvature(1., 1., 1) == approx(1.058, abs=1e-3)


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
    assert raises(LimitError, tas, [5, 0, 0, 0])
    # cannot go to position out of scattering plane
    assert raises(LimitError, tas, [1, 2, 1, 0])
    # cannot go beyond motor limits
    old_limits = psi.userlimits
    psi.userlimits = (0, 50)
    assert raises(LimitError, tas, [1, 0, 0, 1])
    psi.userlimits = old_limits

    # test scattering sense
    tas.scatteringsense = [-1, 1, -1]
    tas.maw([1, 0, 0, 1])
    assert phi() == approx(46.6, abs=0.1)  # now with "+" sign
    assert raises(ConfigurationError, setattr, tas, 'scatteringsense',
                  [2, 0, 2])

    # test energytransferunit
    mono(1)
    ana(2)
    tas.energytransferunit = 'meV'
    assert tas()[3] == approx(-6.216, abs=1e-3)
    tas.energytransferunit = 'THz'
    assert tas()[3] == approx(-1.503, abs=1e-3)
    assert raises(InvalidValueError, setattr, tas, 'energytransferunit', 'A-1')

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
    # assert raises(tas, [1, 0, 0, 1])
    assert raises(ConfigurationError, setattr, tas, 'scanmode', 'BLAH')

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


def test_error_handling(session, log, tas, monkeypatch):
    # check that if one subdev errors out, we wait for the other subdevs
    mfh = session.getDevice('t_mfh')
    phi = session.getDevice('t_phi')

    tas.maw([1.01, 0, 0, 1])
    monkeypatch.setattr(phi, 'speed', 1)
    monkeypatch.setattr(mfh, '_status_exception',
                        PositionError(mfh, 'wrong position'))
    with log.allow_errors():
        try:
            tas.maw([1, 0, 0, 1])
        except MoveError:
            pass
        else:
            assert False, 'PositionError not raised'
        # but we still arrived with phi
        assert phi() == approx(-46.6, abs=0.1)


def test_qscan(session, tas):
    mot = session.getDevice('some_motor')
    qscan((1, 0, 0), Q(0, 0, 0, 0.1), 5, mot, 'scaninfo', t=1)
    qscan((0, 0, 0), (0, 0, 0), 5, 2.5, t_kf=2.662, manual=1,
          h=1, k=1, l=1, e=0, dH=0, dk=0, dl=0, dE=.1)
    qcscan((1, 0, 0), Q(0, 0, 0, 0.1), 3, manual=[1, 2])
    qscan((1, 0, 0), Q(0, 0, 0, 0), 1)

    assert raises(UsageError, qscan, 1, 1, 1)
    assert raises(UsageError, qscan, (1, 0, 0, 0, 0), (0, 0, 0), 10)
    assert raises(UsageError, qscan, (1, 0, 0), (0, 0, 0), 10)
    assert raises(UsageError, qcscan, (1, 0, 0), (0, 0, 0), 10)


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
    assert raises(ErrorLogged, calpos, 1, 0, 0, 1)
    pos()  # still goes to last successful calpos()
    assertPos(tas(), [0.5, 0.5, 0.5, 0])
    rp()  # just check that it works

    assert raises(ComputationError, pos, (1, 2, 3))
    assert raises(LimitError, pos, (0.7, 0.7, 0.7))

    assert raises(UsageError, calpos, 1, 0, 0, 0, 0, 0)
    assert raises(UsageError, pos, 1, 0, 0, 0, 0, 0)


def test_setalign(session, tas):
    pos(.5, .5, .5)
    setalign((-.5, .5, .5))
    assertPos(tas.read(0), [-.5, .5, .5, 0])


def test_checkalign(session, tas):
    tas = session.getDevice('Tas')
    tdet = session.getDevice('vtasdet')
    tas.scanmode = 'CKI'
    tas.scanconstant = 1.57
    checkalign((1, 0, 0), 0.05, 2, tdet, accuracy=0.1)


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

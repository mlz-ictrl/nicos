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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

import pytest

from nicos.core import InvalidValueError, LimitError, MoveError, status
from nicos.devices.generic.slit import Slit

session_setup = 'slit'
Slit._delay = 0.01


def test_slit(session):
    slit = session.getDevice('slit')
    motor_right = session.getDevice('m_right')
    motor_left = session.getDevice('m_left')
    motor_bottom = session.getDevice('m_bottom')
    motor_top = session.getDevice('m_top')

    slit.opmode = '4blades'
    slit.maw([1, 2, 3, 4])
    print([motor_right.doRead(),
           motor_left.doRead(),
           motor_bottom.doRead(),
           motor_top.doRead()])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 2
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert slit.doRead() == [motor_left.doRead(),
                             motor_right.doRead(),
                             motor_bottom.doRead(),
                             motor_top.doRead()]

    slit.reset()
    slit.stop()
    assert slit.doStatus()[0] == status.OK


def test_hgap(session):
    hgap = session.getDevice('hgap')
    motor_right = session.getDevice('m_right')
    motor_left = session.getDevice('m_left')
    hgap.opmode = '2blades'
    hgap.maw([1, 2])
    print([motor_right.doRead(), motor_left.doRead()])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 2
    assert hgap.doRead() == [motor_left.doRead(), motor_right.doRead()]
    hgap.reset()
    hgap.stop()
    assert hgap.doStatus()[0] == status.OK


def test_vgap(session):
    vgap = session.getDevice('vgap')
    motor_bottom = session.getDevice('m_bottom')
    motor_top = session.getDevice('m_top')
    vgap.opmode = '2blades'
    vgap.maw([3, 4])
    print([motor_bottom.doRead(), motor_top.doRead()])
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert vgap.doRead() == [motor_bottom.doRead(), motor_top.doRead()]
    vgap.reset()
    vgap.stop()
    assert vgap.doStatus()[0] == status.OK


def test_slit_opposite(session):
    s2 = session.getDevice('slit2')
    motor_right = session.getDevice('m_right')
    motor_left = session.getDevice('m_left')
    motor_bottom = session.getDevice('m_bottom')
    motor_top = session.getDevice('m_top')

    s2.opmode = '4blades_opposite'
    s2.maw([1, 2, 3, 4])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 2
    assert s2.width.doRead() == 3
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert s2.height.doRead() == 7
    assert s2.doRead() == [1, 2, 3, 4]

    s2.maw([-2.5, 2.5, -2.5, 2.5])
    assert s2.width.doRead() == 0
    assert s2.height.doRead() == 0

    s2.opmode = 'centered'
    s2.maw([5, 5])
    assert motor_left.doRead() == 2.5
    assert motor_right.doRead() == 2.5
    assert motor_bottom.doRead() == 2.5
    assert motor_top.doRead() == 2.5

    s2.opmode = 'offcentered'
    s2.maw([1, 2, 4, 6])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 3
    assert motor_bottom.doRead() == 1
    assert motor_top.doRead() == 5

    pytest.raises(LimitError, s2.start, [1, 2, -1, 0])


def test_hgap_opposite(session):
    sw2 = session.getDevice('hgap2')
    motor_right = session.getDevice('m_right')
    motor_left = session.getDevice('m_left')

    sw2.opmode = '2blades_opposite'
    assert sw2.opmode == '2blades_opposite'
    sw2.maw([6, 7])
    assert motor_left.doRead() == 6
    assert motor_right.doRead() == 7
    assert sw2.width.doRead() == 13
    assert sw2.doRead() == [6, 7]

    sw2.opmode = 'centered'
    sw2.maw([10])
    assert motor_left.doRead() == 5
    assert motor_right.doRead() == 5

    sw2.opmode = 'offcentered'
    sw2.maw([2, 1])
    assert motor_left.doRead() == -1.5
    assert motor_right.doRead() == 2.5

    pytest.raises(LimitError, sw2.start, [1, -1])


def test_vgap_opposite(session):
    sh2 = session.getDevice('vgap2')
    motor_bottom = session.getDevice('m_bottom')
    motor_top = session.getDevice('m_top')

    sh2.opmode = '2blades_opposite'
    sh2.maw([8, 9])
    assert motor_bottom.doRead() == 8
    assert motor_top.doRead() == 9
    assert sh2.height.doRead() == 17
    assert sh2.doRead() == [8, 9]

    sh2.maw([-5, 5])
    assert sh2.height.doRead() == 0

    sh2.opmode = 'centered'
    sh2.maw([10])
    assert motor_bottom.doRead() == 5
    assert motor_top.doRead() == 5

    sh2.opmode = 'offcentered'
    sh2.maw([6, 4])
    assert motor_bottom.doRead() == -4
    assert motor_top.doRead() == 8
    pytest.raises(LimitError, sh2.start, [2, -2])


def test_slit_opmodes(session, log):
    slit = session.getDevice('slit')

    slit.opmode = '4blades'
    slit.maw([8, 9, 4, 5])
    assert slit.read() == [8, 9, 4, 5]
    pytest.raises(InvalidValueError, slit._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, slit.start, [1, 2, 3])
    pytest.raises(InvalidValueError, slit.start, [800, 0])
    pytest.raises(LimitError, slit.start, [8, 8000, 4, 6])
    assert len(slit.valueInfo()) == 4

    slit.maw([8, 10, 4, 7])
    assert slit.read() == [8, 10, 4, 7]

    slit.opmode = 'centered'
    with log.assert_warns():
        slit.read()
    slit.maw([0, 0])
    pytest.raises(InvalidValueError, slit._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, slit.doStart, [800, 0, 0, 0])
    pytest.raises(LimitError, slit.start, [-2, 0])
    pytest.raises(LimitError, slit.start, [0, -2])
    slit.maw([2, 3])
    assert len(slit.valueInfo()) == 2

    slit.opmode = 'offcentered'
    assert slit.read() == [0, 0, 2, 3]
    pytest.raises(InvalidValueError, slit._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, slit.start, [1, 2, 3])
    pytest.raises(InvalidValueError, slit.start, [800, 0])
    pytest.raises(LimitError, slit.start, [-1, -1, 1000, 0])
    slit.maw([5, 1, 4, 4])
    assert slit.read() == [5, 1, 4, 4]
    assert len(slit.valueInfo()) == 4

    slit.opmode = '4blades'
    assert slit.read() == [3, 7, -1, 3]


def test_hgap_opmodes(session, log):
    hgap = session.getDevice('hgap')

    hgap.opmode = '2blades'
    hgap.maw([8, 9])
    assert hgap.read() == [8, 9]
    pytest.raises(InvalidValueError, hgap._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, hgap.start, [1, 2, 3])
    pytest.raises(InvalidValueError, hgap.start, [800])
    pytest.raises(LimitError, hgap.start, [8, 8000])
    assert len(hgap.valueInfo()) == 2

    hgap.maw([8, 10])
    assert hgap.read() == [8, 10]

    hgap.opmode = 'centered'
    with log.assert_warns():
        hgap.read()
    hgap.maw([0])
    pytest.raises(InvalidValueError, hgap._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, hgap.doStart, [800, 0])
    pytest.raises(LimitError, hgap.start, [-2])
    hgap.maw([2])
    assert len(hgap.valueInfo()) == 1

    hgap.opmode = 'offcentered'
    assert hgap.read() == [0, 2]
    pytest.raises(InvalidValueError, hgap._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, hgap.start, [1, 2, 3])
    pytest.raises(InvalidValueError, hgap.start, [800])
    pytest.raises(LimitError, hgap.start, [-1, 1000])
    hgap.maw([5, 4])
    assert hgap.read() == [5, 4]
    assert len(hgap.valueInfo()) == 2

    hgap.opmode = '2blades'
    assert hgap.read() == [3, 7]


def test_vgap_opmodes(session, log):
    vgap = session.getDevice('vgap')

    vgap.opmode = '2blades'
    vgap.maw([4, 5])
    assert vgap.read() == [4, 5]
    pytest.raises(InvalidValueError, vgap._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, vgap.start, [1, 2, 3])
    pytest.raises(InvalidValueError, vgap.start, [800])
    pytest.raises(LimitError, vgap.start, [8, 8000])
    assert len(vgap.valueInfo()) == 2

    vgap.maw([4, 7])
    assert vgap.read() == [4, 7]

    vgap.opmode = 'centered'
    with log.assert_warns():
        vgap.read()
    vgap.maw([0])
    pytest.raises(InvalidValueError, vgap._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, vgap.doStart, [800, 0, 0, 0])
    pytest.raises(LimitError, vgap.start, [-2])
    vgap.maw([3])
    assert len(vgap.valueInfo()) == 1

    vgap.opmode = 'offcentered'
    assert vgap.read() == [0, 3]
    pytest.raises(InvalidValueError, vgap._getPositions, [1, 2, 4])
    pytest.raises(InvalidValueError, vgap.start, [1, 2, 3])
    pytest.raises(InvalidValueError, vgap.start, [800])
    pytest.raises(LimitError, vgap.start, [-1, 1000])
    vgap.maw([1, 4])
    assert vgap.read() == [1, 4]
    assert len(vgap.valueInfo()) == 2

    vgap.opmode = '2blades'
    assert vgap.read() == [-1, 3]


def test_slit_subaxes(session):
    slit = session.getDevice('slit')

    slit.opmode = 'offcentered'
    slit.maw([5, 1, 4, 4])
    assert slit.read() == [5, 1, 4, 4]

    assert slit.centerx() == 5
    assert slit.centery() == 1
    assert slit.width() == 4
    assert slit.height() == 4
    assert slit.left() == 3
    assert slit.right() == 7
    assert slit.bottom() == -1
    assert slit.top() == 3

    slit.centerx.maw(0)
    assert slit.read() == [0, 1, 4, 4]
    slit.centery.maw(0)
    assert slit.read() == [0, 0, 4, 4]
    slit.width.maw(2)
    assert slit.read() == [0, 0, 2, 4]
    slit.height.maw(2)
    assert slit.read() == [0, 0, 2, 2]

    slit.left.maw(-3)
    assert slit.read(0) == [-1, 0, 4, 2]
    slit.right.maw(3)
    assert slit.read(0) == [0, 0, 6, 2]
    slit.bottom.maw(-3)
    assert slit.read(0) == [0, -1, 6, 4]
    slit.top.maw(3)
    assert slit.read(0) == [0, 0, 6, 6]


def test_hgap_subaxes(session, log):
    hgap = session.getDevice('hgap')

    hgap.opmode = 'offcentered'
    hgap.maw([5, 4])
    assert hgap.read() == [5, 4]

    assert hgap.center() == 5
    assert hgap.width() == 4
    assert hgap.left() == 3
    assert hgap.right() == 7

    hgap.center.maw(0)
    assert hgap.read() == [0, 4]
    hgap.width.maw(2)
    assert hgap.read() == [0, 2]

    hgap.left.maw(-3)
    assert hgap.read(0) == [-1, 4]
    hgap.right.maw(3)
    assert hgap.read(0) == [0, 6]


def test_vgap_subaxes(session):
    vgap = session.getDevice('vgap')

    vgap.opmode = 'offcentered'
    vgap.maw([1, 4])
    assert vgap.read() == [1, 4]

    assert vgap.center() == 1
    assert vgap.height() == 4
    assert vgap.bottom() == -1
    assert vgap.top() == 3

    vgap.center.maw(0)
    assert vgap.read() == [0, 4]
    vgap.height.maw(2)
    assert vgap.read() == [0, 2]

    vgap.bottom.maw(-3)
    assert vgap.read(0) == [-1, 4]
    vgap.top.maw(3)
    assert vgap.read(0) == [0, 6]


def test_slit_reference(session, log):
    slit = session.getDevice('slit')
    slit.opmode = '4blades'
    slit.maw([10, 10, 10, 10])
    with log.assert_warns('m_top cannot be referenced'):
        slit.reference()
    # left and right should be referenced
    assert slit.read(0) == [0, 0, 10, 10]

    # this one references in parallel
    slit3 = session.getDevice('slit3')
    slit3.opmode = '4blades'
    slit3.maw([10, 10, 10, 10])
    slit3.reference()
    assert slit3.read(0) == [0, 0, 10, 10]

    slit3.left._ref_error = InvalidValueError('invalid')
    with log.assert_errors('invalid'):
        pytest.raises(MoveError, slit3.reference)


def test_gap_reference(session, log):
    for dev in ('hgap', 'vgap'):
        gap = session.getDevice(dev)
        gap.opmode = '2blades'
        gap.maw([10, 10])
        if dev == 'vgap':
            with log.assert_warns('m_top cannot be referenced'):
                gap.reference()
            assert gap.read(0) == [10, 10]
        else:
            gap.reference()
            assert gap.read(0) == [0, 0]

        # this one references in parallel
        gap3 = session.getDevice(dev + '3')
        gap3.opmode = '2blades'
        gap3.maw([10, 10])
        gap3.reference()

        if dev == 'hgap':
            assert gap3.read(0) == [0, 0]
            gap3.left._ref_error = InvalidValueError('invalid')
            with log.assert_errors('invalid'):
                pytest.raises(MoveError, gap3.reference)
        else:
            assert gap3.read(0) == [10, 10]


def test_slit_fmtstr(session):
    slit = session.getDevice('slit3')
    assert slit.opmode == 'centered'
    assert slit.fmtstr == '%.2f x %.2f'

    # Test the save of the manual changed format
    slit.fmtstr = '%.3f x %.3f'
    assert slit.fmtstr == '%.3f x %.3f'
    slit.opmode = '4blades'
    assert slit.fmtstr != '%.3f x %.3f'
    slit.opmode = 'centered'
    assert slit.fmtstr == '%.3f x %.3f'


def test_gap_fmtstr(session):
    for dev in ('hgap3', 'vgap3'):
        gap = session.getDevice(dev)
        assert gap.opmode == 'centered'
        assert gap.fmtstr == '%.2f'

        # Test the save of the manual changed format
        gap.fmtstr = '%.3f'
        assert gap.fmtstr == '%.3f'
        gap.opmode = '2blades'
        assert gap.fmtstr != '%.3f'
        gap.opmode = 'centered'
        assert gap.fmtstr == '%.3f'


def test_hgap_overlap(session):
    g = session.getDevice('hgap')
    pytest.raises(LimitError, g.width.start, -1)
    goverlap = session.getDevice('hgap_overlap')
    goverlap.width.maw(-1)
    assert goverlap.width() == -1
    assert goverlap._attached_right() == -0.5
    assert goverlap._attached_left() == 0.5
    pytest.raises(LimitError, goverlap.width.start, -2)


def test_vgap_overlap(session):
    g = session.getDevice('vgap')
    pytest.raises(LimitError, g.height.start, -1)
    goverlap = session.getDevice('vgap_overlap')
    goverlap.height.maw(-1)
    assert goverlap.height() == -1
    assert goverlap._attached_bottom() == 0.5
    assert goverlap._attached_top() == -0.5
    pytest.raises(LimitError, goverlap.height.start, -2)


def test_hgap_open(session):
    g = session.getDevice('hgap_open')
    assert g.width() == 0
    g.width.maw(1)
    assert g.width() == 1
    assert g._attached_left() == -0.5
    assert g._attached_right() == 0.5
    pytest.raises(LimitError, g.width.start, 0)


def test_vgap_open(session):
    g = session.getDevice('vgap_open')
    assert g.height() == 0
    g.height.maw(1)
    assert g.height() == 1
    assert g._attached_bottom() == -0.5
    assert g._attached_top() == 0.5
    pytest.raises(LimitError, g.height.start, 0)


def test_two_axis_slit(session):
    slit = session.getDevice('taslit')
    assert slit() == [0, 0]
    assert slit.horizontal() == 0
    assert slit.vertical() == 0

    slit.maw((1, 1))

    slit.reset()

    pytest.raises(InvalidValueError, slit.isAllowed, (1, 2, 3, 4))
    assert not slit.isAllowed([-1, 1])[0]
    pytest.raises(LimitError, slit.move, [-1, 1])

    slit.reference()

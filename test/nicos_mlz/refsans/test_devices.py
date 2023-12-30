# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hereon.de>
#
# *****************************************************************************

"""Module to test custom specific modules."""

import pytest

from nicos.core import status
from nicos.core.errors import ConfigurationError, LimitError

from test.utils import approx, raises

session_setup = 'refsans'


def test_slits(session):
    zb1 = session.getDevice('zb1')
    zb3 = session.getDevice('zb3')
    assert zb1.read(0) == 0.
    assert zb1.mode == 'slit'

    assert zb3.read(0) == [0., 12.]
    assert zb3.mode == 'slit'

    assert zb3.opening.read(0) == 12.
    assert zb3.center.read(0) == 0.

    assert zb3.opening.isAllowed(12.)[0]
    assert zb3.opening.isAllowed(0.)[0]

    zb3.center.maw(10)
    assert zb3.read(0) == [10., 12.]

    zb3.mode = 'point'
    assert zb3.read(0) == [10., 12.]

    assert not zb3.center.isAllowed(20)[0]

    zb3.stop()


def test_beamstop(session):
    hil = session.getDevice('bsh_input_low')
    hi = session.getDevice('bsh_input')
    assert hil.read(0) == 3
    assert hi.read(0) == 3
    assert hi.status(0)[0] == status.OK

    hil.maw(0)
    assert hi.status(0)[0] == status.ERROR

    ci = session.getDevice('bsc_input')
    c = session.getDevice('bsc')
    assert ci.read(0) == 3
    assert c.read(0) == 'None'
    assert c.status(0)[0] == status.ERROR

    ci.maw(5)
    assert c.read(0) == 'Off'
    assert c.status(0)[0] == status.OK

    ci.maw(8)
    assert c.read(0) == 'On'
    assert c.status(0)[0] == status.OK


def test_skewmotor(session):
    bg = session.getDevice('backguard')
    assert bg.skew == 2
    assert bg.precision == 0.1
    assert bg.read(0) == 0
    bg.maw(1)
    bgpos = bg.read(0)
    m1pos = bg._attached_one.read(0)
    m2pos = bg._attached_two.read(0)
    assert bgpos == 1
    assert m1pos == 0
    assert m2pos == 2
    assert bg._attached_one.isAtTarget(m1pos, 0)
    assert bg._attached_two.isAtTarget(m2pos, 2)
    assert bg.isAtTarget(bgpos, 1)


def test_focuspoint(session):
    table = session.getDevice('det_table_a')
    pivot = session.getDevice('det_pivot')
    pivot.maw(9)
    assert pivot.read(0) == 9
    table.maw(9575)
    assert table.read(0) == 9575
    fp = session.getDevice('det_table')
    assert fp.read(0) == 9575
    state = fp.status(0)
    assert state[0] == status.OK
    assert state[1] == 'focus'

    fp.maw(1100)
    state = fp.status(0)
    assert state[0] == status.OK
    assert state[1] == 'idle'


def test_resolution(session):
    rfp = session.getDevice('real_flight_path')
    res = session.getDevice('resolution')
    chopper = session.getDevice('chopper')
    chopper.maw(
        {'D': 22.8, 'chopper2_pos': 5, 'gap': 0.1,
         'wlmax': 21.0, 'wlmin': 3.0, 'manner': 'normal'})
    assert rfp.read(0) == 11.1496
    assert res.read(0) == 6.133


class TestDevices:
    """Test class for the 'simple' REFSANS devices."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        pass

    def test_analog_encoder(self, session):
        dev = session.getDevice('acoder')
        raw = session.getDevice('rawcoder')
        identity = session.getDevice('identitycoder')
        assert dev.read(0) == 1
        assert identity.read(0) == raw.read(0)
        raw.maw(1)
        assert dev.read(0) == 3
        assert identity.read(0) == raw.read(0)
        raw.maw(-1)
        assert dev.read(0) == -1
        assert identity.read(0) == raw.read(0)

    def test_analog_move(self, session):
        raw = session.getDevice('h2_ctrl_l')
        dev = session.getDevice('h2_motor_l')
        assert raw.read(0) == 0
        assert dev.read(0) == 61.6156

        dev.maw(50)

        assert raises(ConfigurationError, session.getDevice, 'h2_motor_r')


class TestChopper:
    """Test class for the REFSANS chopper device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        chopper = session.getDevice('chopper')
        chopper1 = session.getDevice('chopper_speed')
        chopper2 = session.getDevice('chopper2')

        chopper1.maw(0)
        chopper2.pos = 5
        chopper1.maw(1200)

        # test configuration
        assert chopper1.read(0) == 1200
        assert chopper1.read(0) == chopper2.read(0)
        assert chopper2.pos == 5
        assert chopper1.current == 3.2

        target = {'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0,
                  'wlmax': 21.0, 'wlmin': 3.0, 'manner': 'normal'}
        assert chopper.read(0) == target

        yield

        chopper.maw(target)
        chopper1.maw(1200)

    def test_change_chopper2_pos(self, session):
        chopper1 = session.getDevice('chopper_speed')
        chopper2 = session.getDevice('chopper2')

        # not allowed due to chopper speed isn't zero
        assert raises(LimitError, setattr, chopper2, 'pos', 4)

        # all choppers should follow chopper1 in speed
        chopper1.maw(1000)
        assert chopper2.read() == 1000

        # moving speed to zero and allow chopper2 position change
        chopper1.maw(0)
        chopper2.pos = 4
        assert chopper1.current == 0
        chopper1.maw(1000)

    def test_full_chopper_change(self, session):
        chopper = session.getDevice('chopper')
        chopper2 = session.getDevice('chopper2')

        chopper.maw({'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0, 'wlmax': 21.0,
                     'wlmin': 0.0, 'manner': 'normal'})
        assert chopper.read(0) == {'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0,
                                   'wlmax': 21.0, 'wlmin': 0.0,
                                   'manner': 'normal'}
        assert chopper2.phase == 0
        assert chopper.mode == 'normal_mode'

        # check 'chopper_pos == 6' move
        chopper.maw({'D': 22.8, 'chopper2_pos': 6, 'gap': 0.0, 'wlmax': 21.0,
                     'wlmin': 0.0, 'manner': 'normal'})
        # TODO: Reactivate
        # assert chopper.read(0) == {'D': 22.8, 'chopper2_pos': 6, 'gap': 0.0,
        #                            'wlmax': 21.0, 'wlmin': 0.0,
        #                            'manner': 'normal'}
        assert approx(chopper2.phase) == 302.415
        # TODO: Reactivate
        # assert chopper.mode == 'virtual_disc2_pos_6'


class TestDimetixLaser:
    """Class to test the DimetixLaser code."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        signal = session.getDevice('dix_signal')
        yield
        signal.curvalue = 10000

    def test_good_read(self, session):
        """Signal strength is ok."""
        assert session.getDevice('dix').read(0) == 1234

    def test_bad_read(self, session):
        """Signal strength is bad."""
        session.getDevice('dix_signal').curvalue = 7000
        assert session.getDevice('dix').read(0) == -2000


class TestTtr:
    """Class to test Ttr device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        pass

    @pytest.mark.parametrize('unit,expected', [
        ('mbar', 0.0001),
        ('ubar', 0.09982),
        ('torr', 7.51e-05),
        ('mtorr', 0.0748),
        ('micron', 0.0748),
        ('Pa', 0.01002),
        ('kPa', 1.002e-5),
    ])
    def test_read(self, session, unit, expected):
        dev = session.getDevice('ttr')
        dev.unit = unit
        assert dev.read(0) == approx(expected, rel=0.01)


class TestAccuracy:
    """Class to test the Accuracy device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        pass

    @pytest.mark.parametrize('absolute,expected', [
        (True, 10),
        (False, -10),
    ])
    def test_read(self, session, absolute, expected):
        dev = session.getDevice('table_acc')
        dev.absolute = absolute
        assert dev.read(0) == expected

    def test_status(self, session):
        assert session.getDevice('table_acc').status() == (status.OK, '')


class TestDoubleSlitSequence:

    @pytest.fixture(scope='function', autouse=True)
    def slit(self, session):
        slit = session.getDevice('b3')

        yield slit

    def test_read(self, slit, session):
        assert slit.read(0) == [0, 12]

    def test_status(self, slit, session):
        assert slit.status() == (status.OK, 'b3')

    def test_move(self, slit, session):
        assert slit.center.read(0) == 0
        slit.maw([2, 0])
        assert slit.read(0) == [2, 0]
        assert slit.center.read(0) == 2
        slit.maw([0, 0])
        assert slit.read(0) == [0, 0]
        assert slit.center.read(0) == 0

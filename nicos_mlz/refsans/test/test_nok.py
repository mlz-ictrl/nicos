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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Module to test custom specific modules."""

import pytest

from nicos.commands.device import adjust
from nicos.core.errors import ConfigurationError, InvalidValueError, \
    LimitError, UsageError

session_setup = 'refsans'


class TestDoubleNOK:

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        pass

    def test_nok(self, session):
        nok = session.getDevice('nok2')
        assert nok.read(0) == [0, 0]

        # nok.reference()
        nok.maw((1, 1))
        nok.stop()
        # test isAtTarget method
        nok.maw((1, 1))
        assert nok.read(0) == [1, 1]
        assert nok.reactor.read(0) == 1
        assert nok.sample.read(0) == 1

        nok.sample.maw(0)
        nok.reactor.maw(-1)

        pytest.raises(LimitError, nok.maw, (0, 20))
        pytest.raises(LimitError, nok.maw, (-30, -20))


def test_single_nok(session):
    nok1 = session.getDevice('shutter_gamma')
    assert nok1.read(0) == 0

    nok1.maw(1)
    assert nok1.read(0) == 1

    # nok1.reference()


def test_nok_pos(session):
    obs = session.getDevice('obs')
    assert obs.read(0) == 459.
    obs.reset()


def test_nok_inclination_failed(session):
    pytest.raises(ConfigurationError, session.getDevice, 'nok_inc_failed')


class TestSingleSlit:

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        d = session.getDevice('zb1')
        d.mode = 'slit'
        d.offset = 0
        d.maw(0)
        d._setROParam('_offsets', {})
        assert d._offsets == {}

    def test_simple(self, session):
        d = session.getDevice('zb1')
        assert d.read(0) == 0.
        assert d.mode == 'slit'

    def test_change_mode(self, session):
        # Change mode and check positions of slit and motor
        d = session.getDevice('zb1')
        d.mode = 'gisans'
        assert d.read(0) == 100.
        assert d._attached_motor.read(0) == 0.

    def test_change_position(self, session):
        # Move slit and check positions of slit and motor
        d = session.getDevice('zb1')
        d.maw(-5)
        # assert d.read(0) == 95.
        assert d._attached_motor.read(0) == -5.

        # Change mode and check positions of slit and motor
        d.mode = 'gisans'
        # assert d.read(0) == -5.
        # assert d._attached_motor.read(0) == -105.

    def test_stop(self, session):
        # test simply the stop method
        d = session.getDevice('zb1')
        d.stop()

    def test_offsets(self, session):
        d = session.getDevice('zb1')

        # only adjust to new value
        assert d.read(0) == 0
        adjust(d, 0.5)
        # check for offset and mode specific offset
        assert d._offsets['slit'] == -0.5
        assert d.offset == -0.5

        # change mode, maw away and adjust again
        d.mode = 'gisans'
        d.wait()
        # pytest.raises(KeyError, d._offsets['gisans'])
        d.maw(-1)
        adjust(d, 0)
        # check for offset and mode specific offset
        assert d._offsets['gisans'] == -1.5
        assert d.offset == -1.5
        # check for the mode specific offsets
        assert (d._offsets['slit'], d._offsets['gisans']) == (-0.5, -1.5)


class TestDoubleSlit:

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        dev = session.getDevice('zb3')
        dev.mode = 'slit'
        dev.maw([0, 12])

        # check for the same mode of the double slit and attached single slits
        for d in [dev, session.getDevice('zb3r'), session.getDevice('zb3s')]:
            assert d.mode == 'slit'

    def test_changemode(self, session):
        # check that attached single slits follow the mode of double slit
        dev = session.getDevice('zb3')
        dev.mode = 'gisans'
        for d in [dev, session.getDevice('zb3r'), session.getDevice('zb3s')]:
            assert d.mode == 'gisans'

    def test_move(self, session):
        # move to max opening and zero position, check double and single
        # positions
        d, r, s = (session.getDevice('zb3'), session.getDevice('zb3r'),
                   session.getDevice('zb3s'))

        d.maw([0, 12])
        assert d.read(0) == [0, 12]
        assert (r.read(0), s.read(0)) == (0, 0)

        # move to a reduced opening, check double and single positions
        d.maw([0, 6])
        assert d.read(0) == [0, 6]
        assert (r.read(0), s.read(0)) == (-3, 3)

        # move to position with reduced opening
        d.maw([10, 6])
        assert d.read(0) == [10, 6]
        assert (r.read(0), s.read(0)) == (7, 13)

    def test_failures(self, session):
        d = session.getDevice('zb3')
        pytest.raises(InvalidValueError, d.maw, (6, -120))
        pytest.raises(LimitError, d.maw, (-200, 12))

    def test_stop(self, session):
        d = session.getDevice('zb3')
        d.stop()


class TestGap:

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        gap = session.getDevice('h2')
        gap.left.maw(0)
        gap.right.maw(0)

    def test_centered_mode(self, session):
        gap = session.getDevice('h2')
        gap.opmode = 'centered'

        w = 2
        gap.maw([w])
        assert gap.left.read(0) == -w / 2
        assert gap.right.read(0) == w / 2

        assert gap.width.read(0) == w
        assert gap.center.read(0) == 0

        gap.width.maw(10)
        assert gap.read(0) == [10]
        assert gap.left.read(0) == -5
        assert gap.right.read(0) == 5

        pytest.raises(InvalidValueError, gap.maw, [-1, 5])
        pytest.raises(LimitError, gap.maw, [-1])
        pytest.raises(UsageError, gap.center.maw, 1)

    def test_offcentered_mode(self, session):
        gap = session.getDevice('h2')
        gap.opmode = 'offcentered'

        assert gap.read(0) == [0, 0]

        gap.maw((1, 10))
        assert gap.left.read(0) == -4
        assert gap.right.read(0) == 6

        assert gap.width.read(0) == 10
        assert gap.center.read(0) == 1

        pytest.raises(InvalidValueError, gap.maw, [2])
        pytest.raises(LimitError, gap.maw, [1, -1])

    def test_2blades_mode(self, session):
        gap = session.getDevice('h2')
        gap.opmode = '2blades'

        assert gap.read(0) == [0, 0]
        gap.maw([-5, 5])

        assert gap.center.read(0) == 0
        assert gap.width.read(0) == 10

        pytest.raises(InvalidValueError, gap.maw, [2])
        pytest.raises(LimitError, gap.maw, [5, -5])

    def test_2blades_oppsite_mode(self, session):
        gap = session.getDevice('h2')
        gap.opmode = '2blades_opposite'

        assert gap.read(0) == [0, 0]

        gap.maw([5, 5])
        assert gap.width.read(0) == 10
        assert gap.center.read(0) == 0

        pytest.raises(InvalidValueError, gap.maw, [2])

    def test_reset(self, session):
        gap = session.getDevice('h2')
        gap.reset()

    def test_reference(self, session):
        gap = session.getDevice('h2')
        gap.reference()

    def test_change_fmtstr(self, session):
        gap = session.getDevice('h2')
        gap.opmode = 'centered'

        gap.fmtstr = '%.3f'
        assert gap.fmtstr == '%.3f'

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import pytest

from nicos.commands.device import adjust
from nicos.core.errors import ConfigurationError, InvalidValueError, LimitError

from test.utils import raises

session_setup = 'refsans'


def test_nok(session):
    nok2 = session.getDevice('nok2')
    assert nok2.read(0) == [0, 0]

    # nok2.reference()
    nok2.maw((1, 1))
    assert nok2.read(0) == [1, 1]

    assert raises(LimitError, nok2.maw, (0, 20))
    assert raises(LimitError, nok2.maw, (-30, -20))


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
    assert raises(ConfigurationError, session.getDevice, 'nok_inc_failed')


class TestSingleSlit(object):

    @pytest.fixture(scope='function', autouse=True)
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
        assert d.read(0) == 0.
        assert d._attached_motor.read(0) == -100.

    def test_change_position(self, session):
        # Move slit and check positions of slit and motor
        d = session.getDevice('zb1')
        d.maw(-5)
        assert d.read(0) == -5.
        assert d._attached_motor.read(0) == -5.

        # Change mode and check positions of slit and motor
        d.mode = 'gisans'
        assert d.read(0) == -5.
        assert d._attached_motor.read(0) == -105.

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
        # assert raises(KeyError, d._offsets['gisans'])
        d.maw(-1)
        adjust(d, 0)
        # check for offset and mode specific offset
        assert d._offsets['gisans'] == -1
        assert d.offset == -1
        # check for the mode specific offsets
        assert (d._offsets['slit'], d._offsets['gisans']) == (-0.5, -1.)


class TestDoubleSlit(object):

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        dev = session.getDevice('zb3')
        dev.mode = 'slit'
        dev.maw([12, 0])

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
        # move to max opening and zero position, check double and single positions
        d, r, s = (session.getDevice('zb3'), session.getDevice('zb3r'),
                   session.getDevice('zb3s'))

        d.maw([12, 0])
        assert d.read(0) == [12, 0]
        assert (r.read(0), s.read(0)) == (0, 0)

        # move to a reduced opening, check double and single positions
        d.maw([6, 0])
        assert d.read(0) == [6, 0]
        assert (r.read(0), s.read(0)) == (-3, 3)

        # move to position with reduced opening
        d.maw([6, -10])
        assert d.read(0) == [6, -10]
        assert (r.read(0), s.read(0)) == (-13, -7)

    def test_failures(self, session):
        d = session.getDevice('zb3')
        assert raises(InvalidValueError, d.maw, (-10, 0))
        assert raises(LimitError, d.maw, (12, -200))

    def test_stop(self, session):
        d = session.getDevice('zb3')
        d.stop()

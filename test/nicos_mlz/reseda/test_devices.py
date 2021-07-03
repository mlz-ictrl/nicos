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

"""Module to test RESEDA specific modules."""

import pytest

from nicos.core.errors import LimitError

from test.utils import approx, raises

session_setup = 'reseda'


class TestSelector:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        yield
        session.getDevice('selector_speed').maw(0)
        session.getDevice('selcradle').maw(0)

    def test_device(self, session):
        lambda_ = session.getDevice('selector_lambda')
        sel = session.getDevice('selector_speed')
        assert lambda_._get_tilt(0) == 0.0
        assert sel.read(0) == 0
        # if selector not moving the wavelength is negative to indicate zero
        # speed
        assert lambda_.read() == -1

        sel.maw(10000)
        assert lambda_.read(0) == approx(12.7305, abs=0.0001)

        lambda_.maw(6)
        assert sel.read(0) == approx(21218, abs=1)


class TestSelectorSpread:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        yield
        session.getDevice('selector_speed').maw(0)
        session.getDevice('selcradle').maw(0)

    def test_device(self, session):
        lambda_ = session.getDevice('selector_lambda')
        assert lambda_._get_tilt(0) == 0.0
        delta = session.getDevice('selector_delta_lambda')

        # delta lambda should be wavelength independend
        for l in [12, 6]:
            lambda_.maw(l)
            assert delta.read(0) == approx(11.7, abs=0.1)


class TestArmController:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        yield
        session.getDevice('arm1_rot').maw(-55)
        session.getDevice('arm2_rot').maw(0)

    def test_device(self, session):
        _ctrl = session.getDevice('armctrl')
        arm1 = session.getDevice('arm1_rot')
        arm2 = session.getDevice('arm2_rot')
        assert arm1.read(0) == -55
        assert arm2.read(0) == 0

        # too close
        assert raises(LimitError, arm2.maw, -10)
        assert raises(LimitError, arm1.maw, -10)

        # would cross
        assert raises(LimitError, arm1, 5)

        # move arm 1 as close as possible
        arm1.maw(-50)

        # move arm 2 as close as possible
        arm1.maw(-55)
        arm2.maw(-5)

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

from test.utils import approx

session_setup = 'reseda'


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

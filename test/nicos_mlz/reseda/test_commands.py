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

"""RESEDA MIEZE calculation tests."""

from nicos_mlz.reseda.commands import img, miezetau, pol, tof

from test.utils import approx, raises

session_setup = 'reseda'


class TestCommands:

    def test_miezetau(self):

        for f, r in [(1, 1e-6), (10, 1e-5), (100, 1e-4), (1000, 1e-3)]:
            assert approx(miezetau(4.5, f, 3)) == 3.4935644 * r
            assert approx(miezetau(6.0, f, 3)) == 8.2810416 * r

    def test_tof(self, session):
        tof()
        assert session.getDevice('psd_channel').mode == 'tof'

    def test_img(self, session):
        img()
        assert session.getDevice('psd_channel').mode == 'image'

    def test_pol(self, session):
        assert pol(1, 2) == approx(-0.3333, abs=0.0001)
        assert pol(2, 1) == approx(0.3333, abs=0.0001)

        assert raises(ZeroDivisionError, pol, 0, 0)

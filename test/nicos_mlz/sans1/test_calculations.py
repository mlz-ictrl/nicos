#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
"""SANS-1 calculation specific tests."""

from __future__ import absolute_import, division, print_function

from nicos_mlz.sans1.lib.calculations import qrange

from test.utils import approx

session_setup = ''


def test_qrange(session):

    def check_results(res, expected):
        for v, e in zip(res, expected):
            assert v == approx(e, abs=1e-5)

    check_results(qrange(6, 10000, 50, 500), (0.005236, 0.052311))
    check_results(qrange(6, 1200, 50, 500), (0.043605, 0.410745))
    check_results(qrange(6, 20000, 50, 500), (0.002618, 0.026174))

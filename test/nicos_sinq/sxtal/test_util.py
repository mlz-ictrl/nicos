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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import math

from nicos_sinq.sxtal.util import window_integrate


def make_peak(length, center):
    stddev = .5
    profile = []
    for idx in range(length):
        profile.append(100 *
                       math.exp(-(idx - center)**2 / 2. * stddev**2))
    return profile


def test_integrate():
    profile = make_peak(40, 20)
    ok, _, intensity, stddev = window_integrate(profile)
    assert ok
    assert(abs(intensity-482.75) < .2)
    assert(abs(stddev - 22.17) < .1)


def test_no_right():
    profile = make_peak(40, 33)
    ok, reason, _, _ = window_integrate(profile)
    assert(not ok)
    assert(reason == 'No right side')


def test_no_left():
    profile = make_peak(40, 8)
    ok, reason, _, _ = window_integrate(profile)
    assert(not ok)
    assert(reason == 'No left side')

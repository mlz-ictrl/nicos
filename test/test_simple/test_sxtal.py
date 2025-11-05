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

import pytest

from nicos.commands.sample import ClearSamples, NewSample, SelectSample, \
    SetSample

session_setup = 'sxtal'


def assertPos(pos1, pos2):
    for v1, v2 in zip(pos1, pos2):
        assert v1 == pytest.approx(v2, abs=1e-3)


def test_sample_commands(session, log):
    sample = session.experiment.sample

    NewSample('abc', lattice=[60, 40, 30], angles=[90, 90, 90])
    assert sample.samplename == 'abc'
    assert sample.samples == {
        0: {'name': 'abc', 'lattice': [60, 40, 30], 'angles': [90, 90, 90]}}
    assertPos(sample.ubmatrix, [[0.0166, 0, 0],
                                [0, 0.025, 0],
                                [0, 0, 0.0333]])

    SetSample(1, 'def', a=80, b=80, c=80, alpha=90, beta=90, gamma=90)
    assert sample.samples[1] == {
        'name': 'def',
        'a': 80,
        'b': 80,
        'c': 80,
        'alpha': 90,
        'beta': 90,
        'gamma': 90,
    }

    SelectSample(1)
    assert sample.samplename == 'def'
    assert (sample.a, sample.b, sample.c) == (80, 80, 80)
    assert (sample.alpha, sample.beta, sample.gamma) == (90, 90, 90)
    assertPos(sample.ubmatrix, [[0.0125, 0, 0],
                                [0, 0.0125, 0],
                                [0, 0, 0.0125]])

    SelectSample('abc')
    assert sample.samplename == 'abc'
    assert (sample.a, sample.b, sample.c) == (60, 40, 30)
    assertPos(sample.ubmatrix, [[0.0166,  0, 0],
                                [0, 0.025, 0],
                                [0, 0, 0.0333]])

    # Wrong lattice parameter
    NewSample('ghi', lattice=[60, 40, 30, 20])
    assert sample.samplename == 'ghi'
    assertPos(sample.ubmatrix, [[0.2,  0, 0],
                                [0, 0.2, 0],
                                [0, 0, 0.2]])

    # Wrong angles parameter
    NewSample('jkl', angles=[90, 90, 90, 0])
    assert sample.samplename == 'jkl'
    assertPos(sample.ubmatrix, [[0.2,  0, 0],
                                [0, 0.2, 0],
                                [0, 0, 0.2]])

    # No 'a' parameter
    NewSample('mno', b=60)
    assert sample.samplename == 'mno'
    assertPos(sample.ubmatrix, [[0.2,  0, 0],
                                [0, 0.0166, 0],
                                [0, 0, 0.2]])

    ClearSamples()
    assert sample.samples == {}
    assert (sample.a, sample.b, sample.c) == (5, 5, 5)
    assert (sample.alpha, sample.beta, sample.gamma) == (90, 90, 90)
    assertPos(sample.ubmatrix, [[0.2,  0, 0],
                                [0, 0.2, 0],
                                [0, 0, 0.2]])

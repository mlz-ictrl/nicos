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
#
# *****************************************************************************

"""NICOS tests for energy conversion functions."""

from pytest import approx

from nicos.core import ComputationError, ProgrammingError
from nicos.devices.tas import energy
from nicos.devices.tas.mono import from_k, to_k

from test.utils import raises

# input for to/from k tests (input, unit, output)
# note: specify enough precision here for backwards calculation
in_fromk = [(1, 'A', 6.28319),
            (1, 'meV', 2.072123),
            (1, 'THz', 0.501037),
            (0.5, 'A', 12.566370),
            (0.5, 'meV', 0.518031),
            (0.5, 'THz', 0.125259),
            (2, 'A', 3.14159),
            (2, 'meV', 8.28849),
            (2, 'THz', 2.004149),
            ]

in_tok = [(1, 'A', 6.28319),
          (1, 'meV', 0.69469),
          (1, 'THz', 1.4127488),
          (0.5, 'A', 12.56637),
          (0.5, 'meV', 0.49122),
          (0.5, 'THz', 0.99896),
          (2, 'A', 3.14159),
          (2, 'meV', 0.98244),
          (2, 'THz', 1.9979286),
          ]


def test_meV():
    e_mev = energy.Energy(value=81.804165, unit='meV')
    assert float(e_mev.as_lambda()) == approx(1.0)


def test_from_k_raises():
    assert raises(ProgrammingError, from_k, 1, 'MeV')
    assert raises(ComputationError, from_k, 0, 'A')


def test_to_k_raises():
    assert raises(ProgrammingError, to_k, 1, 'MeV')
    assert raises(ComputationError, to_k, 0, 'A')


def test_from_k():
    assert from_k(1, 'A-1') == 1

    # include backward calculations into test
    in_out = in_fromk[:]
    in_out += [(r, u, v) for (v, u, r) in in_tok]

    for args in in_out:
        assert from_k(args[0], args[1]) == approx(args[2], abs=1e-4)


def test_to_k():
    assert to_k(1, 'A-1') == 1
    in_out = in_tok[:]
    in_out += [(r, u, v) for (v, u, r) in in_fromk]

    for args in in_out:
        assert to_k(args[0], args[1]) == approx(args[2], abs=1e-4)


def test_energy_fromk():
    # include backward calculations into test
    in_out = in_fromk[:]
    in_out += [(r, u, v) for (v, u, r) in in_tok]

    for args in in_out:
        e = energy.Energy(value=args[0], unit='A-1')
        assert e.asUnit(args[1]) == approx(args[2], abs=1e-4)


def test_energy_ask():
    # include backward calculations into test
    in_out = in_tok[:]
    in_out += [(r, u, v) for (v, u, r) in in_fromk]

    for args in in_out:
        e = energy.Energy(value=args[0], unit=args[1])
        assert e.asUnit('A-1') == approx(args[2], abs=1e-4)

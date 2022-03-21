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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

session_setup = 'sample'


def test_empty_parameters_use_default(session):
    sample = session.getDevice('Sample')

    sample._prepare_new({})
    assert sample.a == sample.b == sample.c == 6.28
    assert sample.alpha == sample.beta == sample.gamma == 90.0


def test_empty_lattice_use_default(session):
    sample = session.getDevice('Sample')

    sample._prepare_new({'lattice': ()})
    assert sample.a == sample.b == sample.c == 6.28

    sample._prepare_new({'lattice': {'a': 1, 'b': 2}})
    assert sample.a == sample.b == sample.c == 6.28
    assert sample.alpha == sample.beta == sample.gamma == 90.0


def test_valid_lattice(session):
    sample = session.getDevice('Sample')

    sample._prepare_new({'lattice': (1, 2, 3)})
    assert sample.a == 1.
    assert sample.b == 2.
    assert sample.c == 3.
    assert sample.alpha == sample.beta == sample.gamma == 90.0


def test_valid_a_b_c(session):
    sample = session.getDevice('Sample')

    sample._prepare_new({'a': 1.1, 'b': 2.2, 'c': 3.3})
    assert sample.a == 1.1
    assert sample.b == 2.2
    assert sample.c == 3.3
    assert sample.alpha == sample.beta == sample.gamma == 90.0


def test_valid_angles(session):
    sample = session.getDevice('Sample')

    sample._prepare_new({'angles': (91.0, 89.0, 92.0)})
    assert sample.a == sample.b == sample.c == 6.28
    assert sample.alpha == 91
    assert sample.beta == 89
    assert sample.gamma == 92


def test_use_valid_alpha_beta_gamma(session):
    sample = session.getDevice('Sample')

    sample._prepare_new({'alpha': 91.0, 'beta': 89.0, 'gamma': 92.0})
    assert sample.a == sample.b == sample.c == 6.28
    assert sample.alpha == 91
    assert sample.beta == 89
    assert sample.gamma == 92

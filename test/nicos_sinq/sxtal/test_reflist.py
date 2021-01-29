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
import pytest

from nicos.core.errors import InvalidValueError

session_setup = 'sinq_sxtal'


def test_getting_reflist(session):
    sample = session.getDevice('Sample')
    # Test for getting the default reflection list
    tst = sample.getRefList()
    assert(tst is not None)
    # Test for getting a valid reflection list name
    tst = sample.getRefList('mess')
    assert(tst is not None)
    # Test for not getting a reflection list
    assert(not sample.getRefList('hugo'))


def test_adding_reflections(session):
    sample = session.getDevice('Sample')
    ubl = sample.getRefList()
    ubl.clear()
    ubl.append(None, (27.8, 55.9, 127., 234), None)
    ubl.append((2, 0, 0), None, None)
    assert(len(ubl) == 2)


def test_retrieving_reflections(session):
    sample = session.getDevice('Sample')
    ubl = sample.getRefList()
    ubl.clear()
    angles = (27.8, 55.9, 127., 234)
    ubl.append(None, angles, None)
    hkl = (2, 0, 0)
    ubl.append(hkl, None, None)

    with pytest.raises(InvalidValueError):
        ubl.get_reflection(300)

    r = ubl.get_reflection(0)
    for target, val in zip(angles, r[1]):
        assert(abs(target - val) < .01)

    r = ubl.get_reflection(1)
    for target, val in zip(hkl, r[0]):
        assert(abs(target - val) < .01)


def test_mogrify_reflection(session):
    sample = session.getDevice('Sample')
    ubl = sample.getRefList()
    ubl.clear()
    angles = (27.8, 55.9, 127., 234)
    ubl.append(None, angles, None)
    hkl = (1, 0, 0)
    ubl.modify_reflection(0, hkl, None, None)
    r = ubl.get_reflection(0)
    for target, val in zip(angles, r[1]):
        assert (abs(target - val) < .01)
    for target, val in zip(hkl, r[0]):
        assert(abs(target - val) < .01)

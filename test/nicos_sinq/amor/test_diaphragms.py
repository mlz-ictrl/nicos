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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from unittest import TestCase
from unittest.mock import patch

import pytest

from nicos.devices.generic import Slit

pytest.importorskip('epics')

from nicos_sinq.amor.devices.slit import AmorSlitHandler

session_setup = "sinq_amor_diaphragms"


def _make_default_slit_dict(slit_number, left, right, bottom, top):
    return {
        f'd{slit_number}t' : top,
        f'd{slit_number}b': bottom,
        f'd{slit_number}l': left,
        f'd{slit_number}r': right,
    }

_default_values = [

]

def fake_is_active_diaphragm1(*args):
    if args[0] == 'diaphragm1':
        return True
    return False


def fake_is_active_diaphragm2(*args):
    if args[0] == 'diaphragm2':
        return True
    return False


def fake_is_active_diaphragm3(*args):
    if args[0] == 'diaphragm3':
        return True
    return False


def fake_is_active_all_diaphragms(*args):
    if 'diaphragm' in args[0]:
        return True
    return False

# TODO: add more target test
test_targets1 = {
    # did, dih, div
    (0.0,  0.0, 0.0): [('d1l', 0.0), ('d1r', 0.0), ('d1t', 0.0), ('d1b', 0.0)],
}
test_targets2 = {
    # d2d, d2h, d2v
    (0.0,  0.0, 0.0): [('d2l', 0.0), ('d2r', 0.0), ('d2t', 0.0), ('d2b', 0.0)],
}


class TestAmorSlitHandlerController(TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.ctrl = session.getDevice('controller_slm')

    @patch.object(AmorSlitHandler, '_is_active',
                  wraps=fake_is_active_diaphragm1)
    def test_diaphragm1_default_values(self, mock):
        assert isinstance(self.session.getDevice('slit1'), Slit)
        self.session.getDevice('xs')._value = 1.0

        for targets, blades in test_targets1.items():
            for blade in blades:
                self.session.getDevice(blade[0]).curvalue = blade[1]
            values = self.ctrl.read()
            assert values['did'] == targets[0]
            assert values['dih'] == targets[1]
            assert values['div'] == targets[2]

    @patch.object(AmorSlitHandler, '_is_active',
                  wraps=fake_is_active_diaphragm2)
    def test_diaphragm2_default_values(self, mock):
        assert isinstance(self.session.getDevice('slit2'), Slit)

        for targets, blades in test_targets2.items():
            for blade in blades:
                self.session.getDevice(blade[0]).curvalue = blade[1]
            values = self.ctrl.read()
            assert values['d2d'] == targets[0]
            assert values['d2h'] == targets[1]
            assert values['d2v'] == targets[2]

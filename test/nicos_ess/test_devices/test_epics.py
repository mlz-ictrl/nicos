# -*- coding: utf-8 -*-
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
import unittest

import pytest

from test.nicos_ess.test_devices.utils import create_patch

session_setup = 'ess_epics_base'

pytest.importorskip('epics')


class TestReadableDevice(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.mock = create_patch(self,'epics.pv.PV')
        self.device = session.getDevice('DeviceReadable')

    def test_has_read_pv(self):
        assert self.device._get_pv_parameters() == {'readpv'}

    def test_has_readpv_name(self):
        assert self.device._get_pv_name('readpv') == 'TEST:read'


class TestMoveableDevice(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.mock = create_patch(self,'epics.pv.PV')
        self.device = session.getDevice('DeviceMoveable')

    def test_has_read_pv(self):
        assert self.device._get_pv_parameters() == {'readpv', 'writepv'}

    def test_has_readpv_name(self):
        assert self.device._get_pv_name('readpv') == 'TEST:read'
        assert self.device._get_pv_name('writepv') == 'TEST:write'


class TestMoveableDeviceWithTarget(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.mock = create_patch(self, 'epics.pv.PV')
        self.device = session.getDevice('DeviceMoveableWithTarget')

    def test_has_read_pv(self):
        assert self.device._get_pv_parameters() == {'readpv', 'writepv',
                                                    'targetpv'}

    def test_has_readpv_name(self):
        assert self.device._get_pv_name('readpv') == 'TEST:read'
        assert self.device._get_pv_name('writepv') == 'TEST:write'
        assert self.device._get_pv_name('targetpv') == 'TEST:target'

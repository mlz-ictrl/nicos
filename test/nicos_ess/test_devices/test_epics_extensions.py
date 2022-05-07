#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
import pytest

from nicos.core.device import Device
from nicos.devices.epics import EpicsDevice

from nicos_ess.devices.epics.extensions import HasDisablePv

session_setup = 'ess_extensions'


class EpicsDeviceThatHasDisablePv(HasDisablePv, EpicsDevice, Device):
    values = {
        'switchpv:write': 0,
        'switchpv:read': 0,
    }

    def doPreinit(self, mode):
        pass

    def doInit(self, mode):
        pass

    def poll(self, n=0, maxage=0):
        pass

    def _get_pvctrl(self, pvparam, ctrl, default=None, update=False):
        pass

    def _put_pv(self, pvparam, value, wait=False):
        if 'write' in pvparam:
            self.values[pvparam] = value
            self.values['switchpv:read'] = value

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1, timeout=60):
        self._put_pv(pvparam, value)

    def _get_pv(self, pvparam, as_string=False):
        return self.values[pvparam]


class TestHasDisablePv:

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.device = session.getDevice('DeviceCanDisable')
        self.device.values['switchpv:write'] = self.device.switchstates[
            'disable']
        self.device.values['switchpv:read'] = self.device.switchstates[
            'disable']
        self.device._sim_intercept = False

    def test_that_switch_pv_value_equals_switch_state_value_when_enabled(self):
        self.device.values['switchpv:read'] = self.device.switchstates[
            'enable']

        assert self.device._get_pv('switchpv:read') == \
            self.device.switchstates['enable']
        assert self.device.isEnabled

    def test_that_switch_pv_value_equals_switch_state_value_when_disabled(
            self):
        self.device.values['switchpv:read'] = self.device.switchstates[
            'disable']

        assert self.device._get_pv('switchpv:read') == \
            self.device.switchstates['disable']
        assert not self.device.isEnabled

    def test_enable_does_nothing_if_already_enabled(self):
        self.device.values['switchpv:read'] = self.device.switchstates[
            'enable']
        self.device.enable()
        assert self.device.isEnabled

    def test_enable_sets_switchpv_write_if_not_enabled(self):
        self.device.values['switchpv:read'] = self.device.switchstates[
            'disable']

        assert not self.device.isEnabled
        self.device.enable()
        assert self.device.isEnabled

    def test_disable_does_nothing_if_already_disabled(self):
        self.device.values['switchpv:read'] = self.device.switchstates[
            'disable']
        self.device.disable()
        assert not self.device.isEnabled

    def test_enable_sets_switchpv_write_if_not_disabled(self):
        self.device.values['switchpv:read'] = self.device.switchstates[
            'enable']

        assert self.device.isEnabled
        self.device.disable()
        assert not self.device.isEnabled

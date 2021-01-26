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
import unittest
from unittest.mock import patch

import pytest

from nicos.core import ConfigurationError
from nicos.core.device import Device
from nicos.devices.epics import EpicsDevice

from nicos_ess.devices.epics.extensions import HasDisablePv

pytest.importorskip('epics')


session_setup = 'ess_extensions'


class EpicsDeviceThatHasDisablePv(HasDisablePv, EpicsDevice, Device):
    pass


# utility functions

def create_patch(obj, name):
    patcher = patch(name)
    thing = patcher.start()
    obj.addCleanup(patcher.stop)
    return thing


def create_method_patch(reason, obj, name, replacement):
    patcher = patch.object(obj, name, replacement)
    thing = patcher.start()
    reason.addCleanup(patcher.stop)
    return thing


def return_value_wrapper(value):
    def return_value(*args, **kwargs):
        return value
    return return_value


class TestHasDisablePv(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.mock = create_patch(self, 'epics.pv.PV')
        self.device = session.getDevice('DeviceCanDisable')
        self.mock.reset_mock()

    def test_that_switch_pv_value_equals_switch_state_value_when_enabled(self):
        raw_value = self.device.switchstates['enable']
        create_method_patch(self, EpicsDeviceThatHasDisablePv, '_get_pv',
                            return_value_wrapper(raw_value))
        assert self.device._get_pv('switchpv:read') == raw_value
        assert self.device.isEnabled

    def test_that_switch_pv_value_equals_switch_state_value_when_disabled(self):
        raw_value = self.device.switchstates['disable']
        create_method_patch(self, EpicsDeviceThatHasDisablePv, '_get_pv',
                            return_value_wrapper(raw_value))
        assert self.device._get_pv('switchpv:read') == raw_value
        assert not self.device.isEnabled

    def test_is_enabled_raise_exception_if_different_from_switchstates(self):
        raw_value = 'on'
        disable_value = self.device.switchstates['disable']
        enable_value = self.device.switchstates['enable']
        assert not raw_value in [disable_value, enable_value]
        create_method_patch(self, EpicsDeviceThatHasDisablePv, '_get_pv',
                            return_value_wrapper(raw_value))
        with self.assertRaises(Exception) as context:
            assert self.device._get_pv('switchpv:read') == raw_value
            assert not self.device.isEnabled in [disable_value, enable_value]
        assert isinstance(context.exception, ConfigurationError)

    def test_enable_does_nothing_if_already_enabled(self):
        raw_value = self.device.switchstates['enable']
        create_method_patch(self, EpicsDeviceThatHasDisablePv, 'isEnabled',
                            raw_value)
        self.device.enable()
        assert not self.mock.mock_calls

    def test_enable_sets_switchpv_write_if_not_enabled(self):
        disable_value = self.device.switchstates['disable']
        enable_value = self.device.switchstates['enable']
        create_method_patch(self, EpicsDeviceThatHasDisablePv, 'isEnabled',
                            disable_value)
        with patch.object(EpicsDeviceThatHasDisablePv, '_put_pv') as \
                mock_put_pv:
            self.device.enable()
            mock_put_pv.assert_called_once_with('switchpv:write', enable_value)

    def test_disable_does_nothing_if_already_disabled(self):
        raw_value = self.device.switchstates['disable']
        create_method_patch(self, EpicsDeviceThatHasDisablePv, 'isEnabled',
                            raw_value)
        self.device.disable()
        assert not self.mock.mock_calls

    def test_enable_sets_switchpv_write_if_not_disabled(self):
        disable_value = self.device.switchstates['disable']
        enable_value = self.device.switchstates['enable']
        create_method_patch(self, EpicsDeviceThatHasDisablePv, 'isEnabled',
                            enable_value)
        with patch.object(EpicsDeviceThatHasDisablePv, '_put_pv') as \
                mock_put_pv:
            self.device.disable()
            mock_put_pv.assert_called_once_with('switchpv:write', disable_value)

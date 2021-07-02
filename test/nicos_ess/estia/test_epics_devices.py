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
#
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""
Test different ESTIA device
"""

from unittest import TestCase
from unittest.mock import patch

import pytest

from nicos.core import status

pytest.importorskip('epics')
pytest.importorskip('kafka')

from nicos_ess.devices.epics.base import EpicsDeviceEss, EpicsReadableEss
from nicos_ess.estia.devices.pt100 import EpicsPT100Temperature, error_bits, \
    get_pt100_status_message

session_setup = 'estia'


# utility functions
def create_method_patch(reason, obj, name, replacement):
    patcher = patch.object(obj, name, replacement)
    thing = patcher.start()
    reason.addCleanup(patcher.stop)
    return thing


def return_value_wrapper(value):
    def return_value(*args, **kwargs):
        return value
    return return_value


def test_get_pt100_status_message_no_error():
    assert get_pt100_status_message(0) == (status.OK, '')
    for text in set(error_bits.keys()) - {'error'}:
        assert get_pt100_status_message(error_bits[text]) == (status.OK, '')


def test_get_pt100_status_message_error():
    error = 0x40
    assert get_pt100_status_message(error | 0b1) == (status.ERROR, 'underrange')
    assert get_pt100_status_message(error | 0b10) == (status.ERROR, 'overrange')
    assert get_pt100_status_message(error | 0b100) == (status.ERROR, 'limit1 '
                                                                     'overshot')
    assert get_pt100_status_message(error | 0b1000) == (status.ERROR,
                                                        'limit1 undershot')
    assert get_pt100_status_message(error | 0b10000) == (status.ERROR,
                                                         'limit2 overshot')
    assert get_pt100_status_message(error | 0b100000) == (status.ERROR,
                                                          'limit2 undershot')
    assert get_pt100_status_message(error) == (status.ERROR, 'error')


@pytest.mark.skip
@patch('epics.pv.PV')
class TestEpicsPT100(TestCase):
    session = None

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        create_method_patch(self, EpicsDeviceEss, '_get_mapped_epics_status',
                            return_value_wrapper((status.OK, '')))

    def test_status_underrange(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40 | 0b1))
        assert sensor.doStatus() == (status.ERROR, 'underrange')
        sensor._status = (status.UNKNOWN, '')

    def test_status_overrange(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40 | 0b10))
        assert sensor.doStatus() == (status.ERROR, 'overrange')
        sensor._status = (status.UNKNOWN, '')

    def test_status_limit1_undershot(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40 | 0b100))
        assert sensor.doStatus() == (status.ERROR, 'limit1 overshot')
        sensor._status = (status.UNKNOWN, '')

    def test_status_limit1_overshot(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40 | 0b1000))
        assert sensor.doStatus() == (status.ERROR, 'limit1 undershot')
        sensor._status = (status.UNKNOWN, '')

    def test_status_limit2_undershot(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40 | 0b10000))
        assert sensor.doStatus() == (status.ERROR, 'limit2 overshot')
        sensor._status = (status.UNKNOWN, '')

    def test_status_limit2_overshot(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40 | 0b100000))
        assert sensor.doStatus() == (status.ERROR, 'limit2 undershot')
        sensor._status = (status.UNKNOWN, '')

    def test_unknown_error_status(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40))
        assert sensor.doStatus() == (status.ERROR, 'error')

    def test_invalid_status_message_doesn_t_change_device_status(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(0x40))
        assert sensor.doStatus() == (status.ERROR, 'error')
        # test that an invalid status message doesn't change the device status
        create_method_patch(self, EpicsPT100Temperature, '_get_pv',
                            return_value_wrapper(-1))
        assert sensor.doStatus() == (status.ERROR, 'error')
        sensor._status = (status.UNKNOWN, '')

    def test_read_return_read_value_if_statuspv_is_missing(self, mock):
        sensor = self.session.getDevice('temperature_sensor')
        statuspv = sensor.statuspv
        sensor._setROParam('statuspv', None)
        sensor._value = 132
        create_method_patch(self, EpicsReadableEss, 'doRead',
                            return_value_wrapper(42))
        assert sensor.read() == 42
        sensor._setROParam('statuspv', statuspv)

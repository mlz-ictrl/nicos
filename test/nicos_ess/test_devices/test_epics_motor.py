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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

import pytest

from nicos.commands.device import adjust
from nicos.devices.epics.pyepics.motor import EpicsMotor

session_setup = 'ess_motors'


class FakeEpicsMotor(EpicsMotor):
    """
    Epics motor with fake getting and setting of PVs.
    """
    position = 0

    values = {
        'speed': 10,
        'basespeed': 0,
        'maxspeed': 10,
        'position': position,
        'stop': 0,
        'lowlimit': -110,
        'highlimit': 110,
        'readpv': position,
        'writepv': position,
        'offset': 0,
        'enable': 1,
        'direction': 0,
        'resolution': 0,
    }

    def doPreinit(self, mode):
        pass

    def doInit(self, mode):
        pass

    def _get_pvctrl(self, pvparam, ctrl, default=None, update=False):
        pass

    def _put_pv(self, pvparam, value, wait=False):
        self.values[pvparam] = value

        if pvparam == 'offset':
            self.values['lowlimit'] += value
            self.values['highlimit'] += value

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1, timeout=60):
        self.values[pvparam] = value

        if pvparam == 'offset':
            self.values['lowlimit'] += value
            self.values['highlimit'] += value

    def _get_pv(self, pvparam, as_string=False, use_monitor=True):
        return self.values[pvparam]

    def _put_pv_checked(self, pvparam, value, wait=False, update_rate=0.1,
                        timeout=60, precision=0):
        self._put_pv(pvparam, value, wait)


class DerivedEpicsMotor(FakeEpicsMotor):
    def doPreinit(self, mode):
        self._record_fields = dict(FakeEpicsMotor._record_fields)
        self._record_fields.update({'extra_field': 'XTR'})


class TestEpicsMotor:
    motor = None

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.motor = self.session.getDevice('motor1')
        self.motor.values['lowlimit'] = -110
        self.motor.values['highlimit'] = 110
        self.motor.values['basespeed'] = 0
        self.motor.values['maxspeed'] = 10
        self.motor.offset = 0

    def test_adjust_command_sets_offset_correctly(self):
        # Initial offset should be 0
        assert self.motor.offset == 0

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(self.motor, new_pos)

        # Check new offset value
        assert new_pos == -self.motor.offset
        assert new_pos == self.motor.epics_offset

    def test_adjust_command_causes_epics_absolute_limits_to_be_updated(self):
        # Get initial limits
        low, high = self.motor.abslimits
        epics_low, epics_high = self.motor.epics_abslimits

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(self.motor, new_pos)

        # Check new limits
        assert (low, high) == self.motor.abslimits
        assert (epics_low + new_pos, epics_high +
                new_pos) == self.motor.epics_abslimits

    def test_adjust_command_causes_user_limits_to_be_updated(self):
        # Get initial limits
        low, high = self.motor.userlimits

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(self.motor, new_pos)

        # Check new limits
        assert (low + new_pos, high + new_pos) == self.motor.userlimits

    def test_setting_offset_affects_read_offset_correctly(self):
        # Initial offset should be 0
        assert self.motor.offset == 0

        # Set offset
        new_offset = 50
        self.motor.offset = new_offset

        # Check new offset value
        assert new_offset == self.motor.offset

    def test_setting_offset_causes_epics_absolute_limits_to_be_updated(self):
        # Get initial limits
        low, high = self.motor.abslimits
        epics_low, epics_high = self.motor.epics_abslimits

        # Set offset
        new_offset = 50
        self.motor.offset = new_offset

        # Check new limits
        assert (low, high) == self.motor.abslimits
        assert (epics_low - new_offset, epics_high -
                new_offset) == self.motor.epics_abslimits

    def test_setting_offset_causes_user_limits_to_be_updated(self):
        # Get initial limits
        low, high = self.motor.userlimits

        # Set offset
        new_offset = 50
        self.motor.offset = new_offset

        # Check new limits
        assert (low - new_offset,
                high - new_offset) == self.motor.userlimits


class TestDerivedEpicsMotor:
    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.motor1 = self.session.getDevice('motor1')
        self.motor2 = self.session.getDevice('motor2')

    def test_record_fields(self):
        motor1_fields = self.motor1._record_fields
        motor2_fields = self.motor2._record_fields
        difference = set(motor2_fields) ^ set(motor1_fields)
        assert difference

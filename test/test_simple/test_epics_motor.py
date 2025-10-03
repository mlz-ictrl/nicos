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
#   Stefan Mathis <stefan.mathis@psi.eu>
#
# *****************************************************************************

import pytest
import numpy as np
import time
import threading

from nicos.commands.device import adjust
from nicos.core import status, LimitError
from nicos.devices.epics.pva.motor import EpicsMotor

session_setup = 'epics_motor'


class FakeEpicsMotor(EpicsMotor):
    """
    Epics motor with fake getting and setting of PVs.
    """

    hardware_access = False

    # This is equivalent to the DLLM field of the motor record
    _diallowlimit = -110

    # This is equivalent to the DHLM field of the motor record
    _dialhighlimit = 110

    values = {
        'speed': 10,
        'basespeed': 2,
        'maxspeed': 10,
        'stop': 0,
        'lowlimit': _diallowlimit,
        'highlimit': _dialhighlimit,
        'lowlimitswitch': 0,
        'highlimitswitch': 0,
        'softlimit': 0,
        'precision': 0.001,
        'readpv': 0,
        'writepv': 0,
        'offset': 0,
        'enable': 1,
        'miss': 0,
        'direction': 0,
        'resolution': 0,
        'errormsgpv': '',
        'alarm_severity': 0,
        'donemoving': 1,
        'moving': 0,
        'homeforward': 0,
        'homereverse': 0,
        'status': 0,
        'position_deadband': 0,
    }

    def doPreinit(self, mode):
        pass

    def doInit(self, mode):
        pass

    def _get_pvctrl(self, pvparam, ctrl, default=None, update=False):
        pass

    def _put_pv(self, pvparam, value, timeout=None):
        if pvparam == 'offset':
            self.values['lowlimit'] = self._diallowlimit + value
            self.values['highlimit'] = self._dialhighlimit + value
            self.values['readpv'] += value + self.values['offset']
        elif pvparam == 'writepv':
            self.values['readpv'] = value + self.offset
        elif pvparam == 'homeforward' and value == 1:
            self.values['donemoving'] = 0
        elif pvparam == 'homereverse' and value == 1:
            self.values['donemoving'] = 0
        self.values[pvparam] = value

    def _get_pv(self, pvparam, as_string=False, use_monitor=True):
        return self.values[pvparam]

    def doReadUnit(self):
        return 'mm'

    def _reset_test_motor(self):
        # This also updates the limits, therefore it needs to be set first
        self.offset = 0

        self.values['lowlimit'] = self._diallowlimit
        self.values['highlimit'] = self._dialhighlimit
        self.values['basespeed'] = 2
        self.values['maxspeed'] = 10
        self.values['readpv'] = 0
        self.values['moving'] = 0
        self.values['donemoving'] = 1
        self.values['errormsgpv'] = ''
        self.values['alarm_severity'] = 0
        self.values['miss'] = 0
        self.values['softlimit'] = 0
        self.values['highlimitswitch'] = 0
        self.values['lowlimitswitch'] = 0
        self.values['homeforward'] = 0
        self.values['homereverse'] = 0
        self.userlimits = (self.values['lowlimit'], self.values['highlimit'])
        if hasattr(self, '_new_offset'):
            del self._new_offset
        self.values['setpointdeadband'] = 0


class DerivedFakeEpicsMotor(FakeEpicsMotor):
    def doPreinit(self, mode):
        self._record_fields = dict(FakeEpicsMotor._record_fields)
        self._record_fields.update({'extra_field': 'XTR'})
        return FakeEpicsMotor.doPreinit(self, mode)


class DefTest:
    motor = None
    motor_no_opt_pv = None

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.motor = self.session.getDevice('motor1')
        self.motor._reset_test_motor()
        self.motor_no_opt_pv = self.session.getDevice('motor2')
        self.motor_no_opt_pv._reset_test_motor()

    def test_optional_pvs(self):
        assert self.motor.errormsgpv
        assert self.motor.reseterrorpv

        assert not self.motor_no_opt_pv.errormsgpv
        assert not self.motor_no_opt_pv.reseterrorpv

    def test_offset_does_not_shift_abslim(self):
        # Initial offset should be 0
        assert self.motor.offset == 0
        abslim = self.motor.abslimits

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(self.motor, new_pos)

        # The absolute limits as seen from NICOS should not shift
        assert self.motor.abslimits == abslim

        # Redefine current position using 'adjust'
        new_pos = 100
        adjust(self.motor, new_pos)

        # The absolute limits as seen from NICOS should not shift
        assert self.motor.abslimits == abslim

    def test_adjust_command_sets_offset_correctly(self):
        # Initial offset should be 0
        assert self.motor.offset == 0

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(self.motor, new_pos)

        # Check new offset value
        assert new_pos == -self.motor.offset
        assert new_pos == self.motor.epics_offset

        # Redefine current position using 'adjust'
        new_pos = 2000
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
        assert self.motor.read(0) == 0
        adjust(self.motor, new_pos)
        assert self.motor.read(0) == 50

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

        # Set offset
        new_pos = 600
        adjust(self.motor, new_pos)

        # Check new limits
        assert (low, high) == self.motor.abslimits
        assert (low + new_pos, high + new_pos) == self.motor.userlimits

    def test_setting_offset_affects_read_offset_correctly(self):
        # Initial offset should be 0
        assert self.motor.offset == 0

        # Set offset
        new_offset = 50
        self.motor.offset = new_offset

        # Check new offset value
        assert new_offset == self.motor.offset

        # Set offset
        new_offset = 2000
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

        # Set offset
        new_offset = 2000
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

        # Set new custom userlimits
        delta = 10
        self.motor.userlimits = (low - new_offset + delta,
                                 high - new_offset - delta)
        assert (low - new_offset + delta,
                high - new_offset - delta) == self.motor.userlimits

        # Now, the offset is changed again
        new_offset = 2000
        self.motor.offset = new_offset

        # Check new limits
        assert (-2100, -1900) == self.motor.userlimits

    def test_set_speed_limits(self):

        assert self.motor.speedlimits == (2, 10)

        self.motor.speed = 9
        assert self.motor.speed == 9

        self.motor.speed = 1
        assert self.motor.speed == 2

        self.motor.speed = 12
        assert self.motor.speed == 10

    def test_read_speed_limits(self):

        # EPICS denotes "no speed limit" as 0
        self.motor.values['maxspeed'] = 0
        assert self.motor.speedlimits == (2, np.inf)

        self.motor.speed = 1e308
        assert self.motor.speed == 1e308

    def test_move(self):

        # Move motor to defined position. This "movement" happens instantly
        self.motor.maw(10)
        assert self.motor.read() == 10
        assert self.motor.isAtTarget()

        # Set user limits and then try to move outside it
        (minlim, maxlim) = self.motor.userlimits
        with pytest.raises(LimitError):
            self.motor.maw(minlim - 1)

        with pytest.raises(LimitError):
            self.motor.maw(maxlim + 1)

        # Let the motor miss its target (detected via EPICS flag)
        self.motor.maw(5)
        self.motor.values['miss'] = 1
        assert not self.motor.isAtTarget()
        self.motor.values['miss'] = 0

        # Let the motor miss its target (detected by difference between target
        # and actual position)
        self.motor.maw(15)
        self.motor.values['readpv'] = 12
        assert not self.motor.isAtTarget()

    @pytest.mark.timeout(5)
    def test_reference(self):

        def start_reference(motor, runtime):

            def simulate_hardware(motor, runtime):
                time.sleep(runtime)
                motor.values['donemoving'] = 1
                motor.values['homeforward'] = 0
                motor.values['homereverse'] = 0
                motor.values['readpv'] = -100

            # Hardware simulation
            thread = threading.Thread(target=simulate_hardware, args=(self.motor, runtime))
            thread.start()
            motor.reference()

            # Reset parameter anyway
            motor.values['donemoving'] = 1

        # Time the motor needs for its reference run in seconds
        runtime = 0.2

        # Start the reference run
        thread = threading.Thread(target=start_reference, args=(self.motor, runtime))
        thread.start()

        # Wait until the simulated reference run has started
        time.sleep(0.5*runtime)

        # Motor is now doing a reference run
        stat = self.motor.status()
        assert stat[0] == status.BUSY
        assert stat[1]

        # Pause the test until the reference run is done
        thread.join(1)

        if thread.is_alive():
            pytest.fail('Simulated reference run did not finish in expected time')

        # Motor has finished after the reference method returns
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

    def test_status_with_errormsgpv(self):
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set the motor in moving state
        self.motor.values['moving'] = 1
        stat = self.motor.status()
        assert stat[0] == status.BUSY
        assert stat[1]

        # Stop the motor
        self.motor.values['moving'] = 0
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error
        errormsg = 'Something went wrong'
        self.motor.values['errormsgpv'] = errormsg
        self.motor.values['alarm_severity'] = 2
        stat = self.motor.status()
        assert stat[0] == status.ERROR
        assert errormsg in stat[1]

        # Reset the error
        self.motor.values['errormsgpv'] = ''
        self.motor.values['alarm_severity'] = 0
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error while moving
        self.motor.values['moving'] = 1
        errormsg = 'Something went wrong'
        self.motor.values['errormsgpv'] = errormsg
        self.motor.values['alarm_severity'] = 2
        stat = self.motor.status()
        assert stat[0] == status.ERROR
        assert errormsg in stat[1]

        # Reset the error
        self.motor.values['moving'] = 0
        self.motor.values['errormsgpv']  = ''
        self.motor.values['alarm_severity'] = 0
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a high limit switch warning
        self.motor.values['highlimitswitch'] = 1
        stat = self.motor.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        self.motor.values['highlimitswitch'] = 0
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a low limit switch warning
        self.motor.values['lowlimitswitch'] = 1
        stat = self.motor.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        self.motor.values['lowlimitswitch'] = 0
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a soft limit violation
        self.motor.values['softlimit'] = 1
        stat = self.motor.status()
        assert stat[0] == status.WARN
        assert stat[1]

    def test_status_without_errormsgpv(self):

        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set the motor in moving state
        self.motor_no_opt_pv.values['moving'] = 1
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.BUSY
        assert stat[1]

        # Stop the motor
        self.motor_no_opt_pv.values['moving'] = 0
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error
        self.motor_no_opt_pv.values['alarm_severity'] = 2
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.ERROR
        assert self.motor._default_errormsg in stat[1]

        # Reset the error
        self.motor_no_opt_pv.values['alarm_severity'] = 0
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error while moving
        self.motor_no_opt_pv.values['moving'] = 1
        self.motor_no_opt_pv.values['alarm_severity'] = 2
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.ERROR
        assert self.motor._default_errormsg in stat[1]

        # Reset the error
        self.motor_no_opt_pv.values['moving'] = 0
        self.motor_no_opt_pv.values['alarm_severity'] = 0
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a high limit switch warning
        self.motor_no_opt_pv.values['highlimitswitch'] = 1
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        self.motor_no_opt_pv.values['highlimitswitch'] = 0
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a low limit switch warning
        self.motor_no_opt_pv.values['lowlimitswitch'] = 1
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        self.motor_no_opt_pv.values['lowlimitswitch'] = 0
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a soft limit violation
        self.motor_no_opt_pv.values['softlimit'] = 1
        stat = self.motor_no_opt_pv.status()
        assert stat[0] == status.WARN
        assert stat[1]

# This class runs the actual tests
class TestEpicsMotor(DefTest):
    pass

class TestDerivedFakeEpicsMotor:
    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.motor = self.session.getDevice('motor1')
        self.motor_no_opt_pv = self.session.getDevice('motor2')

    def test_record_fields(self):
        motor_fields = self.motor._record_fields
        motor_no_opt_pv_fields = self.motor_no_opt_pv._record_fields
        difference = set(motor_no_opt_pv_fields) ^ set(motor_fields)
        assert difference

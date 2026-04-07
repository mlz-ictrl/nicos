# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
from nicos.devices.epics.motor import EpicsMotor, MSG_VELOCITY, MSG_REFERENCE

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
        'jogspeed': 0,
        'jogforward': 0,
        'jogreverse': 0,
        'position_deadband': 0,
        'rawvelocity': 0,
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
        elif pvparam == 'jogforward' and value == 1:
            self.values['donemoving'] = 0
            self.values['moving'] = 1
        elif pvparam == 'jogreverse' and value == 1:
            self.values['donemoving'] = 0
            self.values['moving'] = 1
        elif pvparam == 'stop' and value == 1:
            self.values['donemoving'] = 1
            self.values['moving'] = 0
            self.values['jogforward'] = 0
            self.values['jogreverse'] = 0
        self.values[pvparam] = value

    def _get_pv(self, pvparam, as_string=False, use_monitor=True):
        return self.values[pvparam]

    def doReadUnit(self):
        unit = 'mm'
        self._populate_velocity_move_unit(unit)
        return unit

    def doReset(self):
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
        self.values['jogspeed'] = 0
        self.values['jogforward'] = 0
        self.values['jogreverse'] = 0
        self.values['status'] = int('0000000000000000', 2)
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

    @pytest.fixture
    def motor(self, session):
        m = session.getDevice('motor1')
        m.reset()
        yield m
        m.reset()

    @pytest.fixture
    def jogmove(self, session):
        return session.getDevice('jogmove1')

    @pytest.fixture
    def motor_no_opt_pv(self, session):
        m = session.getDevice('motor2')
        m.reset()
        yield m
        m.reset()

    def test_optional_pvs(self, motor, motor_no_opt_pv):
        assert motor.errormsgpv
        assert motor.reseterrorpv

        assert not motor_no_opt_pv.errormsgpv
        assert not motor_no_opt_pv.reseterrorpv

    def test_offset_does_not_shift_abslim(self, motor):
        # Initial offset should be 0
        assert motor.offset == 0
        abslim = motor.abslimits

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(motor, new_pos)

        # The absolute limits as seen from NICOS should not shift
        assert motor.abslimits == abslim

        # Redefine current position using 'adjust'
        new_pos = 100
        adjust(motor, new_pos)

        # The absolute limits as seen from NICOS should not shift
        assert motor.abslimits == abslim

    def test_adjust_command_sets_offset_correctly(self, motor):
        # Initial offset should be 0
        assert motor.offset == 0

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(motor, new_pos)

        # Check new offset value
        assert new_pos == -motor.offset
        assert new_pos == motor.epics_offset

        # Redefine current position using 'adjust'
        new_pos = 2000
        adjust(motor, new_pos)

        # Check new offset value
        assert new_pos == -motor.offset
        assert new_pos == motor.epics_offset

    def test_adjust_command_causes_epics_absolute_limits_to_be_updated(self, motor):
        # Get initial limits
        low, high = motor.abslimits
        epics_low, epics_high = motor.epics_abslimits

        # Redefine current position using 'adjust'
        new_pos = 50
        assert motor.read(0) == 0
        adjust(motor, new_pos)
        assert motor.read(0) == 50

        # Check new limits
        assert (low, high) == motor.abslimits
        assert (epics_low + new_pos, epics_high +
                new_pos) == motor.epics_abslimits

    def test_adjust_command_causes_user_limits_to_be_updated(self, motor):
        # Get initial limits
        low, high = motor.userlimits

        # Redefine current position using 'adjust'
        new_pos = 50
        adjust(motor, new_pos)

        # Check new limits
        assert (low + new_pos, high + new_pos) == motor.userlimits

        # Set offset
        new_pos = 600
        adjust(motor, new_pos)

        # Check new limits
        assert (low, high) == motor.abslimits
        assert (low + new_pos, high + new_pos) == motor.userlimits

    def test_setting_offset_affects_read_offset_correctly(self, motor):
        # Initial offset should be 0
        assert motor.offset == 0

        # Set offset
        new_offset = 50
        motor.offset = new_offset

        # Check new offset value
        assert new_offset == motor.offset

        # Set offset
        new_offset = 2000
        motor.offset = new_offset

        # Check new offset value
        assert new_offset == motor.offset

    def test_setting_offset_causes_epics_absolute_limits_to_be_updated(self, motor):
        # Get initial limits
        low, high = motor.abslimits
        epics_low, epics_high = motor.epics_abslimits

        # Set offset
        new_offset = 50
        motor.offset = new_offset

        # Check new limits
        assert (low, high) == motor.abslimits
        assert (epics_low - new_offset, epics_high -
                new_offset) == motor.epics_abslimits

        # Set offset
        new_offset = 2000
        motor.offset = new_offset

        # Check new limits
        assert (low, high) == motor.abslimits
        assert (epics_low - new_offset, epics_high -
                new_offset) == motor.epics_abslimits

    def test_setting_offset_causes_user_limits_to_be_updated(self, motor):
        # Get initial limits
        low, high = motor.userlimits

        # Set offset
        new_offset = 50
        motor.offset = new_offset

        # Check new limits
        assert (low - new_offset,
                high - new_offset) == motor.userlimits

        # Set new custom userlimits
        delta = 10
        motor.userlimits = (low - new_offset + delta,
                            high - new_offset - delta)
        assert (low - new_offset + delta,
                high - new_offset - delta) == motor.userlimits

        # Now, the offset is changed again
        new_offset = 2000
        motor.offset = new_offset

        # Check new limits
        assert (-2100, -1900) == motor.userlimits

    def test_set_speed_limits(self, motor):
        assert motor.speedlimits == (2, 10)

        motor.speed = 9
        assert motor.speed == 9

        with pytest.raises(LimitError):
            motor.speed = 1

        with pytest.raises(LimitError):
            motor.speed = 12

    def test_read_speed_limits(self, motor):
        # EPICS denotes "no speed limit" as 0
        motor.values['maxspeed'] = 0
        assert motor.speedlimits == (2, np.inf)

        motor.speed = 1e308
        assert motor.speed == 1e308

    def test_move(self, motor):
        # Move motor to defined position. This "movement" happens instantly
        motor.maw(10)
        assert motor.read() == 10
        assert motor.isAtTarget()

        # Set user limits and then try to move outside it
        (minlim, maxlim) = motor.userlimits
        with pytest.raises(LimitError):
            motor.maw(minlim - 1)

        with pytest.raises(LimitError):
            motor.maw(maxlim + 1)

        # Let the motor miss its target (detected via EPICS flag)
        motor.maw(5)
        motor.values['miss'] = 1
        assert not motor.isAtTarget()
        motor.values['miss'] = 0

        # Let the motor miss its target (detected by difference between target
        # and actual position)
        motor.maw(15)
        motor.values['readpv'] = 12
        assert not motor.isAtTarget()

    @pytest.mark.timeout(5)
    def test_reference_done_for_some_time(self, motor):

        def reference_run(motor, runtime):
            def simulate_hardware(motor, runtime):
                time.sleep(runtime)
                motor.values['donemoving'] = 1
                motor.values['homeforward'] = 0
                motor.values['homereverse'] = 0
                motor.values['readpv'] = -100

            # Hardware simulation
            thread = threading.Thread(target=simulate_hardware, args=(motor, runtime))
            thread.start()
            motor.reference()

            # Reset parameter anyway
            motor.values['donemoving'] = 1

        # Time the motor needs for its reference run in seconds
        runtime = 0.2

        # Start the reference run
        thread = threading.Thread(target=reference_run, args=(motor, runtime))
        thread.start()

        # Wait until the simulated reference run has started
        time.sleep(0.5*runtime)

        # Motor is now doing a reference run
        stat = motor.status()
        assert stat[0] == status.BUSY
        assert stat[1] == MSG_REFERENCE

        # Pause the test until the reference run is done. Within the motor
        # device, it is checked if the motor reports done_moving for at least
        # a second before homing is finished. Hence, we need to wait a bit more
        # here.
        thread.join(2)

        if thread.is_alive():
            pytest.fail('Simulated reference run did not finish in expected time')

        # Motor has finished after the reference method returns
        stat = motor.status()
        assert stat[0] == status.OK
        assert stat[1] == ''

    @pytest.mark.timeout(5)
    def test_reference_done_at_home(self, motor):

        def reference_run(motor, runtime):
            def simulate_hardware(motor, runtime):
                time.sleep(runtime)
                motor.values['donemoving'] = 1
                motor.values['homeforward'] = 0
                motor.values['homereverse'] = 0
                motor.values['readpv'] = -100
                motor.values['status'] = int('0000000010000000', 2)

            # Hardware simulation
            thread = threading.Thread(target=simulate_hardware, args=(motor, runtime))
            thread.start()
            motor.reference()

        # Time the motor needs for its reference run in seconds
        runtime = 0.2

        # Start the reference run
        thread = threading.Thread(target=reference_run, args=(motor, runtime))
        thread.start()

        # Wait until the simulated reference run has started
        time.sleep(0.5*runtime)

        # Motor is now doing a reference run
        stat = motor.status()
        assert stat[0] == status.BUSY
        assert stat[1] == MSG_REFERENCE

        # Pause the test until the reference run is done. Within the motor
        # device, it is checked if the motor reports done_moving and bit 8 has
        # been set
        thread.join(1)

        if thread.is_alive():
            pytest.fail('Simulated reference run did not finish in expected time')

        # Motor has finished after the reference method returns
        stat = motor.status()
        assert stat[0] == status.OK
        assert stat[1] == 'homed'

    def test_at_home(self, motor):
        stat = motor.status()
        assert stat[0] == status.OK
        assert stat[1] == ''

        # Set to "at home"
        motor.values['status'] = int('0000000010000000', 2)
        stat = motor.status()
        assert stat[0] == status.OK
        assert stat[1] == 'homed'

    def test_status_with_errormsgpv(self, motor):
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set the motor in moving state
        motor.values['moving'] = 1
        stat = motor.status()
        assert stat[0] == status.BUSY
        assert stat[1]

        # Stop the motor
        motor.values['moving'] = 0
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error
        errormsg = 'Something went wrong'
        motor.values['errormsgpv'] = errormsg
        motor.values['alarm_severity'] = 2
        stat = motor.status()
        assert stat[0] == status.ERROR
        assert errormsg in stat[1]

        # Reset the error
        motor.values['errormsgpv'] = ''
        motor.values['alarm_severity'] = 0
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error while moving
        motor.values['moving'] = 1
        errormsg = 'Something went wrong'
        motor.values['errormsgpv'] = errormsg
        motor.values['alarm_severity'] = 2
        stat = motor.status()
        assert stat[0] == status.ERROR
        assert errormsg in stat[1]

        # Reset the error
        motor.values['moving'] = 0
        motor.values['errormsgpv'] = ''
        motor.values['alarm_severity'] = 0
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a high limit switch warning
        motor.values['highlimitswitch'] = 1
        stat = motor.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        motor.values['highlimitswitch'] = 0
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a low limit switch warning
        motor.values['lowlimitswitch'] = 1
        stat = motor.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        motor.values['lowlimitswitch'] = 0
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a soft limit violation
        motor.values['softlimit'] = 1
        stat = motor.status()
        assert stat[0] == status.WARN
        assert stat[1]

    def test_status_without_errormsgpv(self, motor, motor_no_opt_pv):
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set the motor in moving state
        motor_no_opt_pv.values['moving'] = 1
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.BUSY
        assert stat[1]

        # Stop the motor
        motor_no_opt_pv.values['moving'] = 0
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error
        motor_no_opt_pv.values['alarm_severity'] = 2
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.ERROR
        assert motor._default_errormsg in stat[1]

        # Reset the error
        motor_no_opt_pv.values['alarm_severity'] = 0
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set an error while moving
        motor_no_opt_pv.values['moving'] = 1
        motor_no_opt_pv.values['alarm_severity'] = 2
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.ERROR
        assert motor._default_errormsg in stat[1]

        # Reset the error
        motor_no_opt_pv.values['moving'] = 0
        motor_no_opt_pv.values['alarm_severity'] = 0
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a high limit switch warning
        motor_no_opt_pv.values['highlimitswitch'] = 1
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        motor_no_opt_pv.values['highlimitswitch'] = 0
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a low limit switch warning
        motor_no_opt_pv.values['lowlimitswitch'] = 1
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.WARN
        assert stat[1]

        # Reset the warning
        motor_no_opt_pv.values['lowlimitswitch'] = 0
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Set a soft limit violation
        motor_no_opt_pv.values['softlimit'] = 1
        stat = motor_no_opt_pv.status()
        assert stat[0] == status.WARN
        assert stat[1]

    def test_jogmode(self, motor, jogmove):
        # Motor is idle
        stat = motor.status()
        assert stat[0] == status.OK

        # Jogmove forward
        jogmove.start(10)
        stat = motor.status()
        assert stat[0] == status.BUSY
        assert stat[1] == MSG_VELOCITY
        assert motor._get_pv('jogspeed') == 10
        assert motor._get_pv('jogforward') == 1
        assert motor._get_pv('jogreverse') == 0

        # Stop
        motor.stop()
        stat = motor.status()
        assert stat[0] == status.OK
        assert stat[1] == ''
        assert motor._get_pv('jogforward') == 0
        assert motor._get_pv('jogreverse') == 0

        # Jogmove reverse
        jogmove.move(-10)
        stat = motor.status()
        assert stat[0] == status.BUSY
        assert stat[1] == MSG_VELOCITY
        assert motor._get_pv('jogspeed') == 10
        assert motor._get_pv('jogforward') == 0
        assert motor._get_pv('jogreverse') == 1

    def test_read_units(self, motor, jogmove):
        assert motor.unit == 'mm'
        assert motor.parameters['velocity_move'].unit == 'mm / s'
        assert jogmove.unit == 'mm / s'


# This class runs the actual tests
class TestEpicsMotor(DefTest):
    pass


class TestDerivedFakeEpicsMotor:

    @pytest.fixture(autouse=True)
    def motor(self, session):
        m = session.getDevice('motor1')
        m.reset()
        yield m
        m.reset()

    @pytest.fixture(autouse=True)
    def motor_no_opt_pv(self, session):
        m = session.getDevice('motor2')
        m.reset()
        yield m
        m.reset()

    def test_record_fields(self, motor, motor_no_opt_pv):
        motor_fields = motor._record_fields
        motor_no_opt_pv_fields = motor_no_opt_pv._record_fields
        difference = set(motor_no_opt_pv_fields) ^ set(motor_fields)
        assert difference

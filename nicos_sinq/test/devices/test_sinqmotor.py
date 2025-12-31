# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

from nicos.core import status

from nicos.core.errors import UsageError
from nicos_sinq.devices.epics.motor import SinqMotor
from test.test_simple.test_epics_motor import FakeEpicsMotor, DefTest

session_setup = 'sinqmotor'


class FakeSinqMotor(FakeEpicsMotor, SinqMotor):
    """
    Epics motor with fake getting and setting of PVs.
    """

    def doPreinit(self, mode):
        FakeEpicsMotor.doPreinit(self, mode)
        self.values['enable'] = 0
        self.values['enable_rbv'] = 1
        self.values['connected_rbv'] = 1
        self.values['can_disable'] = 1
        self.values['encoder_type'] = 'incremental'

    def _reset_test_motor(self):
        FakeEpicsMotor._reset_test_motor(self)
        self.values['enable'] = 0
        self.values['enable_rbv'] = 1
        self.values['connected_rbv'] = 1
        self.values['can_disable'] = 1
        self.values['encoder_type'] = 'incremental'
        self.inputlimits = self.doReadAbslimits()
        self.delta_limits = (0,0)

    # Suppress subscription of PV callbacks
    def doInit(self, mode):
        pass

# Run the tests from the base class, but use the 'sinq_epics_motor_pva' setup
# Then, some additional tests are run.
class DefTestSinqMotor(DefTest):

    # SinqMotor has no optional PVs, skip the test
    def test_optional_pvs(self):
        pass

    # SinqMotor always has an error message, skip the test
    def test_status_without_errormsgpv(self):
        pass

    def test_defaultpvs(self):
        assert self.motor._get_pv_name('errormsgpv') == self.motor.motorpv + \
               SinqMotor._extension_records['errormsgpv']
        assert self.motor._get_pv_name('reseterrorpv') == self.motor.motorpv + \
               SinqMotor._extension_records['reseterrorpv']

    def test_status_ext(self):

        # Motor is idle
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]
        assert self.motor.enabled
        assert self.motor.connected

        # Motor is disabled
        self.motor.values['enable_rbv'] = 0
        assert not self.motor.enabled
        stat = self.motor.status()
        assert stat[0] == status.DISABLED
        assert stat[1]

        # Motor is disabled AND has an error
        self.motor.values['enable_rbv'] = 0
        self.motor.values['errormsgpv'] = 'TestError'
        self.motor.values['alarm_severity'] = 2
        stat = self.motor.status()
        assert stat[0] == status.ERROR
        assert 'disabled' in stat[1]
        assert 'TestError' in stat[1]
        self.motor.values['errormsgpv'] = ''
        self.motor.values['alarm_severity'] = 0

        # Motor is disconnected
        self.motor.values['connected_rbv'] = 0
        assert not self.motor.connected
        stat = self.motor.status()
        assert stat[0] == status.DISABLED
        assert stat[1]

        # Motor is disconnected AND has an error
        self.motor.values['errormsgpv'] = 'TestError'
        self.motor.values['alarm_severity'] = 2
        stat = self.motor.status()
        print(stat)
        assert stat[0] == status.DISABLED
        assert 'disconnected' in stat[1]
        assert 'TestError' not in stat[1] # Error is not shown if motor is disconnected
        self.motor.values['errormsgpv'] = ''
        self.motor.values['alarm_severity'] = 0

    def test_enable(self):

        # Try to disable a motor which is moving
        self.motor.values['moving'] = 1
        with pytest.raises(UsageError):
            self.motor.disable()
        self.motor.values['moving'] = 0

        # Try to disable a motor which cannot be disabled
        self.motor.values['can_disable'] = 0
        with pytest.raises(UsageError):
            self.motor.disable()

        # A disabled motor which cannot be disabled can still be enabled
        self.motor.values['can_disable'] = 0
        self.motor.values['enable_rbv'] = 1
        self.motor.enable()

    @pytest.mark.timeout(5)
    def test_reference_absolute(self):
        self.motor.values['encoder_type'] = 'absolute'

        # Motors with absolute encoders do not perform a reference run
        self.motor.reference()
        stat = self.motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

class TestSinqmotor1(DefTestSinqMotor):
    motor = None

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.motor = self.session.getDevice('motor1')
        self.motor._reset_test_motor()

class TestsSinqMotor2(DefTestSinqMotor):
    motor = None

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.motor = self.session.getDevice('motor2')
        self.motor._reset_test_motor()

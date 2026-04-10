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

from nicos.core import status

from nicos.core.errors import UsageError
from nicos_sinq.devices.epics.motor import SinqMotor
from test.test_simple.test_epics_motor import FakeEpicsMotor, DefTest

session_setup = 'sinqmotor'


class FakeSinqMotor(FakeEpicsMotor, SinqMotor):
    """
    Epics motor with fake getting and setting of PVs.
    """

    def doReset(self):
        FakeEpicsMotor.doReset(self)
        self.values['enable'] = 0
        self.values['enable_rbv'] = 1
        self.values['connected_rbv'] = 1
        self.values['can_disable'] = 1
        self.values['encoder_type'] = 'incremental'
        self.values['fixifnothomed'] = 0
        self.inputlimits = self.doReadAbslimits()
        self.delta_limits = (0, 0)

    def doPreinit(self, mode):
        self.doReset()

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

    def test_defaultpvs(self, motor):
        assert motor._get_pv_name('errormsgpv') == motor.motorpv + \
               SinqMotor._extension_records['errormsgpv']
        assert motor._get_pv_name('reseterrorpv') == motor.motorpv + \
               SinqMotor._extension_records['reseterrorpv']

    def test_status_ext(self, motor):

        # Motor is idle
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]
        assert motor.enabled
        assert motor.connected

        # Motor is disabled
        motor.values['enable_rbv'] = 0
        assert not motor.enabled
        stat = motor.status()
        assert stat[0] == status.DISABLED
        assert stat[1]

        # Motor is disabled AND has an error
        motor.values['enable_rbv'] = 0
        motor.values['errormsgpv'] = 'TestError'
        motor.values['alarm_severity'] = 2
        stat = motor.status()
        assert stat[0] == status.ERROR
        assert 'disabled' in stat[1]
        assert 'TestError' in stat[1]
        motor.values['errormsgpv'] = ''
        motor.values['alarm_severity'] = 0

        # Motor is disconnected
        motor.values['connected_rbv'] = 0
        assert not motor.connected
        stat = motor.status()
        assert stat[0] == status.DISABLED
        assert stat[1]

        # Motor is disconnected AND has an error
        motor.values['errormsgpv'] = 'TestError'
        motor.values['alarm_severity'] = 2
        stat = motor.status()
        assert stat[0] == status.DISABLED
        assert 'disconnected' in stat[1]
        assert 'TestError' not in stat[1]  # Error is not shown if motor is disconnected
        motor.values['errormsgpv'] = ''
        motor.values['alarm_severity'] = 0

    def test_enable(self, motor):

        # Try to disable a motor which is moving
        motor.values['moving'] = 1
        with pytest.raises(UsageError):
            motor.disable()
        motor.values['moving'] = 0

        # Try to disable a motor which cannot be disabled
        motor.values['can_disable'] = 0
        with pytest.raises(UsageError):
            motor.disable()

        # A disabled motor which cannot be disabled can still be enabled
        motor.values['can_disable'] = 0
        motor.values['enable_rbv'] = 1
        motor.enable()

    @pytest.mark.timeout(5)
    def test_reference_absolute(self, motor):
        motor.values['encoder_type'] = 'absolute'

        # Motors with absolute encoders do not perform a reference run
        motor.reference()
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

    def test_not_homed(self, motor):
        # Motor is not homed
        motor.values['status'] = int('0000000000000000', 2)
        assert not motor.homed

        # Motor is not homed, but also not fixed if it hasn't been homed
        motor.values['fixifnothomed'] = 0
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]

        # Now motor is fixed within the EPICS driver if it hasn't been homed yet
        motor.values['fixifnothomed'] = 1
        stat = motor.status()
        assert stat[0] == status.WARN
        assert stat[1] == 'Motor needs to be referenced'

        # Set the "homed" bit in the status PV - warning disappears
        motor.values['status'] = int('0100000000000000', 2)
        assert motor.homed
        stat = motor.status()
        assert stat[0] == status.OK
        assert not stat[1]


class TestSinqmotor1(DefTestSinqMotor):

    pass


class TestsSinqMotor2(DefTestSinqMotor):

    @pytest.fixture
    def motor(self, session):
        m = session.getDevice('motor2')
        m.reset()
        yield m
        m.reset()

    @pytest.fixture
    def jogmove(self, session):
        return session.getDevice('jogmove2')

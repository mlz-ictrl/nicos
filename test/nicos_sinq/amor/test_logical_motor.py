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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import sys
import time
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from nicos.core import LimitError, status

from test.utils import ErrorLogged, approx, raises

session_setup = 'sinq_amor_logical_motors'

logical_motors = ['m2t', 's2t', 'ath']

rawdistances = {
    'polariser': 7983,
    'slit1': 7550,
    'slit2': 7145,
    'slit3': 6445,
    'sample': 5310,
    'slit4': 4210,
    'filter': 7727,
    'analyser': 2463,
    'detector': 572
}

initial_positions = [('d1t', 10.000), ('d2t', 10.000), ('d3t', 10.000),
                     ('d4t', 10.000)]

test_targets = {
    # m2t = 0.1, rest at 0.0
    (0.100, 0.000, 0.000): [('soz', -4.801), ('d1b', -5.000),
                            ('d2b', -5.531), ('d3b', -7.318), ('aoz', -8.688),
                            ('aom', -0.100), ('com', -0.100), ('cox', 0.006),
                            ('coz', -11.961), ('d4b', -10.646)],
    # s2t = 0.1 rest at 0.0
    (0.000, 0.100, 0.000): [('soz', 0.000), ('d1b', -5.000),
                            ('d2b', -5.000), ('d3b', -5.000), ('aoz', 3.887),
                            ('aom', 0.100), ('com', 0.100), ('cox', 0.006),
                            ('coz', 7.159), ('d4b', -4.155)],

    # ath = 0.1, rest at 0.0
    (0.000, 0.000, 0.100): [('soz', 0.000), ('d1b', -5.000),
                            ('d2b', -5.000), ('d3b', -5.000), ('aoz', 0.000),
                            ('aom', 0.100), ('com', 0.200), ('cox', 0.011),
                            ('coz', 6.545), ('d4b', -5.000)],

    # m2t = 0.1 and s2t = 0.1
    (0.100, 0.100, 0.000): [('soz', -4.801), ('d1b', -5.000),
                            ('d2b', -5.531), ('d3b', -7.318), ('aoz', -4.801),
                            ('aom', 0.000), ('com', 0.000), ('cox', 0.000),
                            ('coz', -4.801), ('d4b', -9.801)],

    # m2t = 0.1 and ath = 0.1
    (0.100, 0.000, 0.100): [('soz', -4.801), ('d1b', -5.000),
                            ('d2b', -5.531), ('d3b', -7.318), ('aoz', -8.688),
                            ('aom', 0.000), ('com', 0.100), ('cox', 0.006),
                            ('coz', -5.416), ('d4b', -10.646)],

    # s2t = 0.1 and ath = 0.1
    (0.000, 0.100, 0.100): [('soz', 0.000), ('d1b', -5.000),
                            ('d2b', -5.000), ('d3b', -5.000), ('aoz', 3.887),
                            ('aom', 0.200), ('com', 0.300), ('cox', 0.029),
                            ('coz', 13.704), ('d4b', -4.155)],

    # all at 0.1
    (0.100, 0.100, 0.100): [('soz', -4.801), ('d1b', -5.000),
                            ('d2b', -5.531), ('d3b', -7.318), ('aoz', -4.801),
                            ('aom', 0.100), ('com', 0.200), ('cox', 0.011),
                            ('coz', 1.744), ('d4b', -9.801)],

    # m2t = 0.7, s2t = 0.5 and ath = 1.0
    (0.700, 0.500, 1.000): [('soz', -33.611), ('d1b', -5.000),
                            ('d2b', -8.714), ('d3b', -21.225),
                            ('aoz', -41.385), ('aom', 0.800), ('com', 1.800),
                            ('cox', 0.939), ('coz', 17.510), ('d4b', -40.301)],

    # m2t = 1.7, s2t = 0.8 and ath = 0.4
    (1.700, 0.800, 0.400): [('soz', -81.648), ('d1b', -5.000),
                            ('d2b', -14.023), ('d3b', -44.414),
                            ('aoz', -116.632), ('aom', -0.500),
                            ('com', -0.100), ('cox', 0.278), ('coz', -119.904),
                            ('d4b', -94.251)],

    # m2t = -0.3, s2t = 0.7 and ath = -1.0
    (-0.30, 0.700, -1.00): [('soz', 14.404), ('d1b', -5.000),
                            ('d2b', -3.408), ('d3b', 1.953),
                            ('aoz', 53.277), ('aom', 0.000),
                            ('com', -1.000), ('cox', 0.625), ('coz', 20.559),
                            ('d4b', 17.853)],
}


@pytest.mark.skipif('--sinq' not in sys.argv, reason='Only valid for SINQ')
class TestLogicalMotor:
    m2t = None
    s2t = None
    ath = None
    controller = None
    distances = None

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        """
        Initialize the devices, bring them to initial positions, set the
        component distances
        """
        # Set the component distances
        self.distances = session.getDevice('Distances')
        self.distances.rawdistances = rawdistances
        for comp in self.distances._components():
            self.distances._update_component(comp)

        # Set the initial position of devices
        for devname, position in initial_positions:
            dev = session.getDevice(devname)
            dev.maw(position)

        # Initialize the logical motors
        self.m2t = session.getDevice('m2t')
        self.s2t = session.getDevice('s2t')
        self.ath = session.getDevice('ath')
        self.controller = session.getDevice('controller')

    @pytest.mark.parametrize("motortype", logical_motors)
    def test_motor_move_status_is_busy(self, motortype):
        motor = getattr(self, motortype)

        # Test motor status when moving
        motor.move(0.5)
        assert motor.status()[0] == status.BUSY
        motor.stop()

    @pytest.mark.parametrize("motortype", logical_motors)
    def test_motor_stop_target(self, motortype):
        motor = getattr(self, motortype)

        motor.move(0.5)

        # Test motor stop behavior
        motor.stop()
        assert motor.target == approx(motor.read())

        # Let the targets update
        time.sleep(2)

        # Continue the movement of motor and check if it reaches target
        motor.maw(0.5)
        assert motor.read() == approx(0.5, abs=1e-3)

    @pytest.mark.parametrize("motortype", logical_motors)
    def test_out_of_bounds_errors_out(self, motortype):
        motor = getattr(self, motortype)

        llm, hlm = motor.abslimits

        # Test the limits
        assert raises(LimitError, motor, llm - 0.1)
        assert motor.target == approx(motor.read())
        assert raises(LimitError, motor, hlm + 0.1)
        assert motor.target == approx(motor.read())

        # Test that even below limits, if slave motors can't move
        # error is produced
        assert raises(ErrorLogged, motor, llm + 0.1)
        assert motor.target == approx(motor.read())
        assert raises(ErrorLogged, motor, hlm - 0.1)
        assert motor.target == approx(motor.read())

    @pytest.mark.parametrize("targets", test_targets.keys())
    def test_motor_has_correct_targets(self, targets, session):
        # Move the motors to targets
        ml = self.controller._get_move_list({
            'm2t': targets[0],
            's2t': targets[1],
            'ath': targets[2]
        })

        for dev, targ in ml:
            dev = dev.name
            found = False
            for d, t in test_targets[targets]:
                if d == dev:
                    assert t == approx(targ, abs=1e-2), '%s target mismatch' % d
                    found = True
            assert found, 'unexpectedly moved %s' % dev

    def test_analyzer_off_behaviour(self, session):
        # Turn off the analyzer component
        self.distances.__dict__['analyser'] = 'NOT ACTIVE'

        # The slave positions at ath = 0.0 should be same as when ath = 0.1
        self.m2t.maw(0.1)
        self.s2t.maw(0.1)
        self.ath.maw(0.1)
        for slavename, target in test_targets[(0.100, 0.100, 0.000)]:
            slave = session.getDevice(slavename)
            assert slave.read() == approx(target, abs=1e-2)


def create_method_patch(reason, obj, name, replacement):
    patcher = patch.object(obj, name, replacement)
    thing = patcher.start()
    reason.addCleanup(patcher.stop)
    return thing


def return_value_wrapper(value):
    def return_value(*args, **kwargs):
        return value
    return return_value


class TestDetectorAngleMotor(TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session

    def test_do_start(self):
        nu = self.session.getDevice('nu')
        nu._attached_com = Mock()
        nu._attached_coz = Mock()

        target = 45
        expected_coz = 1 * nu.coz_scale_factor

        nu.start(target)
        coz_target = nu._attached_coz.start.call_args[0]
        com_target = nu._attached_com.start.call_args[0]

        assert com_target[0] == -target
        assert coz_target[0] == approx(expected_coz, abs=0.01)

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""
Tests for the counter type detectors in SINQ
"""

import time

import pytest

from nicos.core import status

session_setup = "sinq_amor_counter"


class TestCounter(object):
    """
    Tests for the operations of EL737 counter box in SINQ
    """

    detector = None
    timepreset = None
    countpreset = None
    elapsedtime = None
    counters = []

    @pytest.fixture(autouse=True)
    def initialize_devices(self, sinq_counter, session):
        """
        Initialize the devices if they are not already initialized
        """
        if not self.detector:
            self.detector = session.getDevice(sinq_counter)
        if not self.timepreset:
            self.timepreset = session.getDevice('timepreset')
        if not self.countpreset:
            self.countpreset = session.getDevice('countpreset')
        if not self.elapsedtime:
            self.elapsedtime = session.getDevice('elapsedtime')
        if not self.counters:
            self.counters = [session.getDevice('c%d' % i) for i in range(1, 9)]
        yield
        self.detector.resume()

    def test_set_time_preset(self):
        """
        Test that the time preset is set properly. As only one of either time
        or count preset is used, the count preset should be 0
        """
        self.detector.setPreset(t=5.5)
        time.sleep(1)
        assert self.timepreset.read(0)[0] == 5.5
        assert self.countpreset.read(0)[0] == 0

    def test_set_count_preset(self):
        """
        Test that the count preset is set properly. As only one of either time
        or count preset is used, the time preset should be 0
        """
        self.detector.setPreset(n=1000)
        time.sleep(1)
        assert self.countpreset.read(0)[0] == 1000
        assert self.timepreset.read(0)[0] == 0.0

    def test_set_both_preset(self):
        """
        Test that when both preset are set, count preset is used. As only one
        of either time or count preset is used, the time preset should be 0
        """
        self.detector.setPreset(t=4.5, n=2000)
        time.sleep(1)
        assert self.countpreset.read(0)[0] == 2000
        assert self.timepreset.read(0)[0] == 0

    def test_time_preset_operations(self):
        """
        Test various conditions in count operation when the time preset
        is used
        """
        self.detector.start(t=5)
        assert self.detector.status()[0] == status.BUSY
        time.sleep(5)  # Let it finish counting
        assert self.detector.status()[0] == status.OK
        assert self.elapsedtime.read(0)[0] == 5.0

    def test_count_preset_operations(self):
        """
        Test various conditions in count operation when count preset
        is used
        """
        self.detector.start(n=3500)
        assert self.detector.status()[0] == status.BUSY
        time.sleep(3.5)  # Let it finish counting
        assert self.detector.status()[0] == status.OK
        assert self.counters[0].read(0)[0] == 3500

    def test_stop_count(self):
        """
        Test that the count is interrupted after the detector is stopped
        """
        self.detector.start(t=5)
        self.detector.stop()
        time.sleep(1)
        assert self.elapsedtime.read(0)[0] < 5
        assert self.detector.status() == (status.OK, 'Idle')

    def test_pause_count(self):
        """
        Test that the counting is properly paused and resumed
        """
        self.detector.start(t=20)
        self.detector.pause()
        time.sleep(1)
        assert self.elapsedtime.read(0)[0] < 20
        assert self.detector.status() == (status.OK, 'Paused')
        self.detector.resume()
        time.sleep(1)
        assert self.detector.status()[0] == status.BUSY
        time.sleep(20)
        assert self.detector.status()[0] == status.OK
        assert self.elapsedtime.read(0)[0] == 20.0

    def test_pause_stop(self):
        """
        Test that after the counting is paused followed by stop,
        the status should be OK and not paused
        """
        self.detector.start(t=20)
        self.detector.pause()
        self.detector.stop()
        time.sleep(1)
        assert self.detector.status() == (status.OK, 'Idle')
        self.detector.resume()

    @pytest.mark.parametrize('fail_type', ['XS', 'XD', 'XR'])
    def test_failure(self, session, fail_type):
        """
        Tests the failure conditions on the counter box and once the
        recover is set the counter box should come back to normal.

        Failures tested here:
        XS: Counter fails to start
        XD: Read failure on counter
        XR: Failed while counting
        """

        # Send the failures
        asyn_controller = session.getDevice('cter1')
        asyn_controller.execute(fail_type)

        # Starting the counter should error out
        self.detector.start(t=20)
        time.sleep(10)
        assert self.detector.status()[0] == status.ERROR
        time.sleep(90)  # Let the counter come to recoverable state
        # Set the counter to be recoverable
        asyn_controller.execute('RC')
        self.detector.start(t=10)
        time.sleep(10)

        assert self.detector.status()[0] == status.OK
        assert self.elapsedtime.read(0)[0] == 10.0

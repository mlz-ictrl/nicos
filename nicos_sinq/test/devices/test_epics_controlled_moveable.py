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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import pytest

from nicos.core import status
from nicos.core.errors import LimitError
from nicos_sinq.devices.epics.extensions_pva import EpicsControlledAnalogMoveable

session_setup = 'epics_controlled_moveable'


class FakeEpicsControlledAnalogMoveable(EpicsControlledAnalogMoveable):

    _writeval = 0
    _readval = 0
    _targetval = 0
    _readyval = 1
    _stopval = 1
    _minval = 0
    _maxval = 10
    _starting = False

    def doPreinit(self, mode):
        pass

    def doInit(self, mode):
        self._reset()

    def _get_pvctrl(self, pvparam, ctrl, default=None, update=False):
        pass

    def doReadUnit(self):
        return ''

    def doReadAbslimits(self):
        return (self._minval, self._maxval)

    def _put_pv(self, pvparam, value, wait=False):
        if pvparam == 'writepv':
            self._writeval = value
            self._readval = value
            self._targetval = value
            self._starting = True
        if pvparam == 'stoppv':
            self._stopval = 1
        if pvparam == 'targetpv':
            self._targetval = value

    def _put_pv_blocking(self, pvparam, value, timeout=60):
        self._put_pv(self, pvparam, value)

    def _get_pv(self, pvparam, as_string=False, use_monitor=True):
        if pvparam == 'writepv':
            return self._writeval
        elif pvparam == 'readpv':
            return self._readval
        elif pvparam == 'targetpv':
            return self._targetval
        elif pvparam == 'readypv':
            return self._readyval

    def _put_pv_checked(self, pvparam, value, wait=False, timeout=60,
                        precision=0):
        self._put_pv(pvparam, value, wait)

    def _reset(self):
        self._writeval = 0
        self._readval = 0
        self._targetval = 0
        self._readyval = 1
        self._stopval = 0
        self._minval = 0
        self._maxval = 10
        self._starting = False

    # This method in nicos.devices.epics.pva.epics_devices.EpicsDevice accesses
    # the Python wrapper, which does not exist in the test. The test device
    # cannot have a hardware error.
    def get_alarm_status(self, pvparam):
        return status.OK, ''


class Test:

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.moveable = self.session.getDevice('moveable')
        self.moveable._reset()
        self.moveable_no_opt = self.session.getDevice('moveable_no_opt')
        self.moveable_no_opt._reset()
        self.moveable_no_stoppv = self.session.getDevice('moveable_no_stoppv')
        self.moveable_no_stoppv._reset()

    def test_optional_pvs(self):
        assert self.moveable.stoppv
        assert self.moveable.readypv
        assert self.moveable.targetpv

        assert not self.moveable_no_opt.stoppv
        assert not self.moveable_no_opt.readypv
        assert not self.moveable_no_opt.targetpv

        assert not self.moveable_no_stoppv.stoppv
        assert self.moveable_no_stoppv.readypv
        assert not self.moveable_no_stoppv.targetpv

    def test_move(self):
        assert self.moveable.read(0) == 0
        assert self.moveable.status(0)[0] == status.OK
        self.moveable.move(10)
        assert self.moveable.read(0) == 10
        assert self.moveable.status(0)[0] == status.OK

        # Now the test assumes that the device is still doing sth. and therefore
        # not ready to move yet
        self.moveable._readyval = 0
        assert self.moveable.status(0)[0] == status.BUSY

        with pytest.raises(LimitError):
            self.moveable.move(5)

        # Device is ready to move again
        self.moveable._readyval = 1
        assert self.moveable.read(0) == 10
        assert self.moveable.status(0)[0] == status.OK
        self.moveable.move(5)
        assert self.moveable.read(0) == 5
        assert self.moveable.status(0)[0] == status.OK

        # Try to move outside limits
        with pytest.raises(LimitError):
            self.moveable.move(15)
        with pytest.raises(LimitError):
            self.moveable.move(-5)

    def test_busy_when_target_not_equal_current_value(self):
        # If the device target is not equal to its current position, it should
        # report busy regardless of whether the readypv is set or not
        assert self.moveable.target == 0
        assert self.moveable.read(0) == 0

        self.moveable._put_pv('targetpv', 10)

        # Even though the readypv is 1, the device is still busy, because
        # current position != target
        assert self.moveable.target == 10
        assert self.moveable.read(0) == 0
        assert self.moveable._get_pv('readypv') == 1
        assert self.moveable.status(0)[0] == status.BUSY

    def test_stop_moveable(self):

        # If the device has a stoppv, use this PV everytime
        assert self.moveable._stopval == 0
        assert not self.moveable._starting
        self.moveable.stop()
        assert self.moveable._stopval == 1
        assert not self.moveable._starting

    def test_stop_moveable_no_opt(self):
        # If neither readypv nor stoppv are given, `EpicsControlledAnalogMoveable` should
        # behave like `EpicsAnalogMoveable` (attempt to move to current postion)
        assert not self.moveable_no_opt._starting
        self.moveable_no_opt.stop()
        assert self.moveable_no_opt._starting

    def test_stop_moveable_no_stoppvpv(self):

        # If a readypv, but no stoppv is given, the move attempt is only done if
        # the device is busy
        assert not self.moveable_no_stoppv._starting
        self.moveable_no_opt.stop()
        assert not self.moveable_no_stoppv._starting

        # Make the device busy
        self.moveable_no_stoppv._readyval = 0
        assert self.moveable_no_stoppv.status(0)[0] == status.BUSY
        self.moveable_no_stoppv.stop()
        assert self.moveable_no_stoppv._starting

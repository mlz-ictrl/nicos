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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS commands tests with respect to set 'requires'."""

import pytest

from nicos.commands.device import set  # pylint: disable=redefined-builtin
from nicos.commands.device import disable, move, stop, wait
from nicos.core import GUEST, AccessError, status as devstatus

session_setup = 'device'


class TestDevicePriviledged:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        """Prepare a clean setup for each test on device commands."""
        motor = session.getDevice('mot')

        yield

        motor.speed = 0
        motor.maw(0)

    @pytest.mark.timeout(timeout=60, method='thread', func_only=True)
    def test_stop_privileged(self, session, log):
        # Change the user level to lower access rights to check that the stop
        # on higher level requesting devices will be ignored
        motor = session.getDevice('mot')
        pdev = session.getDevice('privdev')
        speed = pdev.speed
        pdev.speed = motor.speed = 0.1
        move(pdev, 10, motor, 10)
        with session.withUserLevel(GUEST):
            assert pdev.status(0)[0] == devstatus.BUSY
            assert motor.status(0)[0] == devstatus.BUSY
            pytest.raises(AccessError, pdev.stop)
            stop(pdev, motor)
            wait(motor)
            assert motor.status(0)[0] == devstatus.OK
            assert pdev.status(0)[0] == devstatus.BUSY
        stop(pdev)
        wait(pdev)
        assert pdev.status(0)[0] == devstatus.OK
        pdev.speed = motor.speed = speed

    def test_privileged_parameters(self, session, log):
        """Check "requires" restrictions for setting parameters."""
        pdev = session.getDevice('privdev')
        with session.withUserLevel(GUEST):
            pytest.raises(AccessError, set, pdev, 'unit', 'foo')

    def test_privileged_disable(self, session, log):
        """Check "requires" restrictions to disable device."""
        pdev = session.getDevice('privdev')
        with session.withUserLevel(GUEST):
            pytest.raises(AccessError, disable, pdev)

    def test_privileged_start(self, session, log):
        """Check "requires" restrictions to move device."""
        pdev = session.getDevice('privdev')
        with session.withUserLevel(GUEST):
            pytest.raises(AccessError, move, pdev, 1)

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2017 by the NICOS contributors (see AUTHORS)
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
#  Bjoern Pedersen <bjoern,pedersen@frm2.tum.de>
#
# *****************************************************************************
"""
Test for multiwait
"""
import pytest

from nicos.core.utils import multiWait
from nicos.core.errors import TimeoutError, MoveError

from test.utils import raises


session_setup = 'multiwait'


class TestMultiWait(object):

    @pytest.fixture()
    def devices(self, session):
        dev1 = session.getDevice('dev1')
        dev1._value = 1
        dev1._status_exception = None
        dev1._iscompleted_exception =  None

        dev2 = session.getDevice('dev2')
        dev2._value = 2
        dev2._status_exception = None
        dev2._iscompleted_exception =  None

        dev3 = session.getDevice('dev3')
        dev3._value = 3
        dev3._status_exception = None
        dev3._iscompleted_exception =  None

        dev4 = session.getDevice('dev5')
        return [dev1, dev2, dev3, dev4]

    def test_multiwait_retval(self, devices):

        dev1, dev2, dev3, dev4 = devices
        res = multiWait([dev1, dev2, dev3, dev4])

        assert res == {dev1: 1, dev2: 2, dev3: 3}

    def test_multiwait_raising_single_status(self, log, devices):
        dev1, dev2, dev3, dev4 = devices
        dev1._status_exception = TimeoutError('Test message')

        with log.allow_errors():
            assert raises(MoveError, multiWait, [dev1, dev2, dev3, dev4])

    def test_multiwait_raising_single_isCompleted(self, log, devices):
        dev1, dev2, dev3, dev4 = devices
        dev2._iscompleted_exception = TimeoutError('Test 2')

        with log.allow_errors():
            assert raises(TimeoutError, multiWait, [dev1, dev2, dev3, dev4])

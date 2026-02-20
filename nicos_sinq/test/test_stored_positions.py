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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import pytest

from nicos.core.errors import NicosError
from nicos.core.utils import multiWait

from test.utils import ErrorLogged

session_setup = 'stopo'


class TestStoredPositions:

    @pytest.fixture(autouse=True)
    def stopo(self, session):
        v1 = session.getDevice('v1')
        v1.speed = 0
        v1.precision = .1
        v3 = session.getDevice('v3')
        v3.precision = .1

        stopo = session.getDevice('stopo')

        v1.start(3.3)
        v3.start(7.7)
        multiWait([v1, v3])

        yield stopo

        stopo.clear()

    def test_defines_fails(self, session, stopo):
        pytest.raises(ErrorLogged, stopo.define_position, 'p1', ('v4', 2.2), ('v3', 5.5))
        pytest.raises(ErrorLogged, stopo.define_position, 'p3', ('v1', 7), ('v3', 8.4))

    def test_undefined_positions(self, stopo):
        pytest.raises(NicosError, stopo.maw, 'gurke')

    def test_stop(self, stopo):
        stopo.stop()

    def test_undefined_pos(self, session, stopo):
        v1 = session.getDevice('v1')

        pytest.raises(NicosError, stopo.move, 'p1')
        stopo.define_position('p1', ('v1', 2.2), ('v3', 5.5))

        v1.maw(1)
        assert stopo.read(0) == 'Undefined'

    def test_stored_positions(self, session, log, stopo):
        v1 = session.getDevice('v1')
        v3 = session.getDevice('v3')

        stopo.define_position('p1', ('v1', 2.2), ('v3', 5.5))
        stopo.define_position('p2', v1, v3)
        stopo.define_position('p3', v1=1.7, v3=8.4)

        with log.assert_msg_matches([
            r'Name  Device positions',
            r'====  ==========================',
            r"p1    \[\('v1', 2.2\), \('v3', 5.5\)\]",
            r"p2    \[\('v1', 3.3\), \('v3', 7.7\)\]",
            r"p3    \[\('v1', 1.7\), \('v3', 8.4\)\]",
        ]):
            stopo.show()

        for target in ('p1', 'p2', 'p3'):
            stopo.maw(target)
            assert stopo.read(0) == target
            assert v1.isAtTarget()
            assert v3.isAtTarget()
            stopo.stop()

        stopo.delete('p1')
        with log.assert_msg_matches([
            r'Name  Device positions',
            r'====  ==========================',
            r"p2    \[\('v1', 3.3\), \('v3', 7.7\)\]",
            r"p3    \[\('v1', 1.7\), \('v3', 8.4\)\]",
        ]):
            stopo.show()

        pytest.raises(NicosError, stopo.maw, 'p1')

        stopo.clear()
        with log.assert_msg_matches([
            r'Name  Device positions',
            r'====  ================',
        ]):
            stopo.show()
        pytest.raises(NicosError, stopo.maw, 'p2')

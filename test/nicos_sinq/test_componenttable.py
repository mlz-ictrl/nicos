# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

from nicos.commands.basic import AddSetup

session_setup = 'sinq_componenttable'


@pytest.fixture(scope='function', autouse=True)
def init_boatest(session):
    AddSetup('detector', 'stdsystem')


def test_standard(session):
    table = session.getDevice('table_test')
    devList = table.getTableDevices()

    assert len(devList) == 2
    assert 'rb' in devList
    assert 'rc' in devList


def test_adding_setup(session):
    table = session.getDevice('table_test')
    table.attach('stdsystem')
    devList = table.getTableDevices()

    assert len(devList) == 6
    for d in ['rb', 'rc', 'Exp', 'Sample']:
        assert d in devList


def test_removing_setup(session):
    table = session.getDevice('table_test')
    table.attach('stdsystem')
    table.detach('stdsystem')
    devList = table.getTableDevices()

    assert len(devList) == 2
    assert 'rb' in devList
    assert 'rc' in devList


def test_adding_device(session):
    table = session.getDevice('table_test')
    table.attach(session.getDevice('Exp'))

    devList = table.getTableDevices()

    assert len(devList) == 3
    for d in ['rb', 'rc', 'Exp']:
        assert d in devList


def test_removing_device(session):
    table = session.getDevice('table_test')
    exp = session.getDevice('Exp')
    table.attach(exp)
    table.detach('Exp')

    devList = table.getTableDevices()

    assert len(devList) == 2
    assert 'rb' in devList
    assert 'rc' in devList


def test_show(session, log):
    table = session.getDevice('table_test')
    table.attach(session.getDevice('Exp'))
    # table.attach(session.getDevice('detector'))

    with log.assert_msg_matches([r'Standard Devices:',
                                 r'rb, rc',
                                 r'Setups:',
                                 r'Additional Devices',
                                 r'\tExp',
                                 r'Total Devices',
                                 r'rb, rc, Exp',
                                ]):
        table.show()

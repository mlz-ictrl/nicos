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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

"""ANDES specific monochromator exchange tests."""

from nicos.core import UsageError, status

from test.utils import raises

session_setup = 'lahn_monoexchange'


def test_monoblock(session):
    session.getDevice('y1').maw(5)
    session.getDevice('xi1').maw(1)
    session.getDevice('alpha1').maw(3)
    monoblock = session.getDevice('Si')
    assert monoblock.tran == 5 and monoblock.incl == 1 and monoblock.curv == 3
    assert monoblock.read(0) == [5, 1, 3]


def test_exchange(session):
    exchange = session.getDevice('crystal')
    assert exchange._monoblock == session.getDevice('mb1')
    # exchange monoblock
    exchange.maw('Ge')
    assert exchange._monoblock != session.getDevice('mb1')
    exchange.maw('PG')
    assert exchange._monoblock == session.getDevice('mb3')


def test_exchange_focus(session):
    exchange = session.getDevice('crystal')
    # setFocus()
    exchange.setFocus(tran=10, incl=0.1, curv=2)
    monoblock = session.getDevice('Si')
    assert monoblock.tran == 10 and monoblock.incl == 0.1 and monoblock.curv == 2
    # setFocus() changing the order of the arguments
    exchange.setFocus(curv=1, tran=1, incl=1)
    assert monoblock.tran == 1 and monoblock.incl == 1 and monoblock.curv == 1
    # setFocus() with only one argument
    exchange.setFocus(tran=5)
    assert monoblock.tran == 5 and monoblock.incl == 1 and monoblock.curv == 1
    # setFocus() with two arguments
    exchange.setFocus(tran=0, curv=0)
    assert monoblock.tran == 0 and monoblock.incl == 1 and monoblock.curv == 0


def test_exchange_errors(session):
    exchange = session.getDevice('crystal')
    # no arguments
    assert raises(UsageError, exchange.setFocus, )
    # wrong device name
    assert raises(UsageError, exchange.setFocus, blah=10)
    assert raises(UsageError, exchange.setFocus, tran=10, blah=10)


def test_exchange_fallback_blockingmoves_1(session):
    exchange = session.getDevice('crystal')
    z = session.getDevice('meZ')
    z.maw(35)
    assert exchange.status()[0] == status.UNKNOWN
    # blocking monoblock moves
    exchange.setFocus(tran=5)
    assert exchange._monoblock.tran == 0


def test_exchange_fallback_blockingmoves_2(session):
    exchange = session.getDevice('crystal')
    z = session.getDevice('meZ')
    z.curstatus = (status.BUSY, 'busy')
    assert exchange.status()[0] != status.OK
    # blocking monoblock moves
    exchange.setFocus(tran=5)
    assert exchange._monoblock.tran == 0


def test_exchange_fallback_initialization(session):
    z = session.getDevice('meZ')
    z.maw(35)
    exchange = session.getDevice('crystal')
    assert exchange.status()[0] == status.UNKNOWN
    assert exchange._monoblock is None

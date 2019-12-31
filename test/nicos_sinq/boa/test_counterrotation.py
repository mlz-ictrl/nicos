#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

session_setup = 'sinq_counterrotation'


def test_counterrot1(session):
    """This test reproduces the behaviour of the equivalent device in SICS."""
    rbu = session.getDevice('rbu')
    rb = session.getDevice('rb')
    rc = session.getDevice('rc')

    rb.maw(3)
    rc.maw(0)

    rbu.maw(5.)
    assert rbu.read() == 5.
    assert rb.read() == 8.
    assert rc.read() == -5.

    rbu.maw(7)
    assert rbu.read() == 7.
    assert rb.read() == 10.
    assert rc.read() == -7.

    rbu.maw(-5)
    assert rbu.read() == -5.
    assert rb.read() == -2.
    assert rc.read() == 5.

    # Simulate stopping
    rbu.maw(5.)
    rbu.stop()
    rb.curvalue = 7.
    rc.curvalue =  -3.

    assert rbu.read() == 3.5

    # Simulate a rerun
    rbu.maw(7.)

    assert rbu.read() == 7.
    assert rb.read() == 9.
    assert rc.read() == -5.

    # Simulate a restart
    rbu.slave_offset = 1.
    rbu.maw(7.)
    session.destroyDevice('rbu')
    rbu = session.getDevice('rbu')
    assert rbu.read() == 7.

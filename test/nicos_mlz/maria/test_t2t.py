#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""MARIA specific 2 theta unit tests."""

session_setup = "t2t"


def test_maria_t2t(session):
    omega = session.getDevice("omega")
    detarm = session.getDevice("detarm")
    t2t = session.getDevice("t2t")

    target = 2
    slavepos = t2t.scale * target
    t2t.maw(target)
    assert t2t.read(0) == [target, slavepos]
    assert omega.read(0) == target
    assert detarm.read(0) == slavepos
    assert t2t.isAtTarget(target)

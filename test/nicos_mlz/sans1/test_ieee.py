#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""SANS-1 specific device tests."""

from __future__ import absolute_import, division, print_function

from nicos.core import status

session_setup = 'sans1'


def test_ieeedevice(session):
    dev1 = session.getDevice('dev1')
    dev1.maw(10)

    ieee1 = session.getDevice('ieee1')
    assert ieee1.read() == ''  # pylint: disable=compare-to-empty-string
    assert ieee1.status()[0] == status.OK

    assert session.getDevice('ieee2').read() == dev1.read()
    assert session.getDevice('ieee3').read() == dev1.curvalue

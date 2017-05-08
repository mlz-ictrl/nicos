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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""SPODI specific data sink tests."""

from os import path

from nicos.commands.measure import count

import pytest

session_setup = 'spodi'
exp_dataroot = 'spodidata'


@pytest.yield_fixture(scope='class', autouse=True)
def prepare(session, dataroot):
    session.experiment.setDetectors(['adet'])
    # Create devices needed in data sinks
    for dev in ['omgs', 'tths']:
        session.getDevice(dev)
    count(resosteps=1, t=0.01)
    count(resosteps=1, mon1=100)
    yield


class TestSinks(object):

    def test_caress_sink(self, session):
        caressfile = path.join(session.experiment.datapath, 'm100000043.ctxt')
        assert path.isfile(caressfile)

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

"""STRESS-SPEC specific data sink tests."""

from os import path

from nicos.commands.measure import count
from nicos.utils.stubs import generate_stubs

import pytest

try:
    import configobj
except ImportError:
    configobj = None

generate_stubs()

session_setup = 'refsans'
exp_dataroot = 'refsansdata'


@pytest.yield_fixture(scope='class', autouse=True)
def prepare(session, dataroot):
    session.experiment.setDetectors(['det'])
    for d in ['nok1', 'nok2', 'zb0', 'shutter', 'vacuum_CB', 'table',
              'tube', 'h2_center', 'h2_width', 'pivot', 'top_phi']:
        session.getDevice(d)

    # Perform different scans
    count(t=0.01)

    yield


class TestSinks(object):

    @pytest.mark.skipif(not configobj,
                        reason='configobj libraries missing')
    def test_config_sink(self, session):
        cfgfile = path.join(session.experiment.datapath, 'p1234_00000043.cfg')
        assert path.isfile(cfgfile)
        contents = configobj.ConfigObj(cfgfile)
        assert len(contents['NOKs']) == 2

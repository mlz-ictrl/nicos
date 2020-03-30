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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""REFSANS specific data sink tests."""

from __future__ import absolute_import, division, print_function

from os import path

import pytest

from nicos.commands.measure import count

try:
    import configobj  # pylint: disable=unused-import
except ImportError:
    configobj = None

session_setup = 'refsans'
exp_dataroot = 'refsansdata'


@pytest.fixture(scope='class', autouse=True)
def prepare(session, dataroot):
    """Prepare a dataset for refsans"""

    session.experiment.setDetectors(['det'])

    for dev in ['shutter_gamma', 'nok2', 'zb0', 'shutter', 'vacuum_CB',
                'table', 'tube',
                # 'h2.center', 'h2.height',
                'det_pivot', 'top_phi', 'chopper',
                'gonio_theta', 'User2Voltage', 'det', 'det_pivot', 'zb3',
                'zb3r_acc', 'zb3s_acc']:
        session.getDevice(dev)
    count(t=0.01)

    yield


class TestSinks(object):

    @pytest.mark.skipif(configobj is None, reason='configobj library missing')
    def test_config_sink(self, session):
        datafile = path.join(session.experiment.datapath, 'p1234_00000043.cfg')
        assert path.isfile(datafile)
        contents = configobj.ConfigObj(datafile)
        assert len(contents['NOKs']) == 2

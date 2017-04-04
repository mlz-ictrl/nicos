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

import os
import shutil
import time

from os import path

from nicos import config
from nicos.commands.measure import count
from nicos.utils import updateFileCounter
from nicos.utils.stubs import generate_stubs

import pytest

try:
    import configobj
except ImportError:
    configobj = None

session_setup = 'refsans'

year = time.strftime('%Y')
generate_stubs()


@pytest.fixture(scope='module', autouse=True)
def cleanup(session):
    exp = session.experiment
    exp.finish()
    assert exp.detlist == []
    dataroot = path.join(config.nicos_root, 'refsansdata')
    if path.exists(dataroot):
        shutil.rmtree(dataroot)
    os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    open(counter, 'w').close()
    updateFileCounter(counter, 'point', 42)

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser', localcontact=exp.localcontact)
    exp.sample.new({'name': 'mysample'})
    exp.setEnvironment([])

    # Check the correct detector setup
    det = session.getDevice('det')
    assert len(det._attached_timers) == 1
    assert len(det._attached_counters) == 2
    assert len(det._attached_monitors) == 1
    assert len(det._attached_images) == 1
    exp.setDetectors([det])
    assert exp.detlist == ['det']

    assert path.abspath(exp.datapath) == path.abspath(
        path.join(config.nicos_root, 'refsansdata', year, 'p1234', 'data'))

    for d in ['nok1', 'nok2', 'zb0', 'shutter', 'vacuum_CB', 'table',
              'tube', 'h2_center', 'h2_width', 'pivot', 'top_phi',]:
        _ = session.getDevice(d)
    # Perform different scans
    count(t=1)

    yield
    exp.finish()


@pytest.mark.skipif(not configobj,
                    reason='configobj libraries missing')
def test_config_sink(session):
    cfgfile = path.join(session.experiment.datapath, 'p1234_00000043.cfg')
    assert path.isfile(cfgfile)
    contents = configobj.ConfigObj(cfgfile)
    assert len(contents['NOKs']) == 2

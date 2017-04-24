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

"""TOFTOF specific data sink tests."""

import os
import time

from os import path

from nicos import config
from nicos.commands.measure import count
from nicos.utils import updateFileCounter

import pytest

session_setup = 'toftof'

year = time.strftime('%Y')


@pytest.yield_fixture(scope='module', autouse=True)
def cleanup(session):
    exp = session.experiment
    exp.finish()
    exp.setDetectors([])
    assert exp.detlist == []
    dataroot = path.join(config.nicos_root, 'toftofdata')
    os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    open(counter, 'w').close()
    updateFileCounter(counter, 'point', 42)

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser', localcontact=exp.localcontact)
    exp.sample.new({'name': 'mysample'})
    exp.setEnvironment([])

    det = session.getDevice('det')
    assert len(det._attached_timers) == 1
    assert len(det._attached_counters) == 0
    assert len(det._attached_monitors) == 1
    assert len(det._attached_images) == 1
    exp.setDetectors([det])
    assert exp.detlist == ['det']

    B = session.getDevice('B')
    P = session.getDevice('P')
    T = session.getDevice('T')
    exp.setEnvironment([B, P, T])

    assert path.abspath(exp.datapath) == path.abspath(
        path.join(dataroot, year, 'p1234', 'data'))

    # Create devices needed in data sinks
    for dev in ['slit', 'vac0', 'vac1', 'vac2', 'vac3', 'gx', 'gy', 'gz',
                'gphi', 'gcx', 'gcy']:
        session.getDevice(dev)

    rc = session.getDevice('rc')
    rc.maw('on')
    assert rc.read(0) == 'on'

    assert session.getDevice('chRatio').read(0) == 1
    assert session.getDevice('chCRC').read(0) == 1
    assert session.getDevice('chST').read(0) == 1

    for disc in ['d1', 'd2', 'd3', 'd4', 'd6', 'd7']:
        assert session.getDevice(disc).read(0) == 6000
    assert session.getDevice('d5').read(0) == -6000

    chSpeed = session.getDevice('chSpeed')
    chSpeed.maw(6000)
    assert chSpeed.read(0) == 6000

    chWL = session.getDevice('chWL')
    assert chWL.read(0) == 4.5

    ngc = session.getDevice('ngc')
    ngc.maw('focus')
    assert ngc.read(0) == 'focus'

    count(t=0.01)
    count(mon1=1)

    yield


def test_toftof_sink(session):
    toftoffile = path.join(session.experiment.datapath, '00000043_0000.raw')
    assert path.isfile(toftoffile)

    logfile = path.join(session.experiment.datapath, '00000043_0000.log')
    assert path.isfile(logfile)

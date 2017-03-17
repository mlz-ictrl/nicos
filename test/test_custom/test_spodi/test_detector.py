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

import os
import shutil
import time

from os import path

from nicos import config
from nicos.commands.measure import count
from nicos.utils import updateFileCounter

import pytest

session_setup = 'spodi'

year = time.strftime('%Y')


@pytest.fixture(scope='module', autouse=True)
def cleanup(session):
    exp = session.experiment
    exp.finish()
    exp.setDetectors([])
    assert exp.detlist == []
    dataroot = path.join(config.nicos_root, 'spodidata')
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

    # Check correct detector configuration
    basedet = session.getDevice('basedet')
    assert len(basedet._attached_timers) == 1
    assert len(basedet._attached_counters) == 0
    assert len(basedet._attached_monitors) == 1
    assert len(basedet._attached_images) == 1
    adet = session.getDevice('adet')
    exp.setDetectors([adet])
    assert exp.detlist == ['adet']

    assert path.abspath(exp.datapath) == path.abspath(
        path.join(config.nicos_root, 'spodidata', year, 'p1234', 'data'))

    # Move the detector to a distinct position and check it
    tths = session.getDevice('tths')
    tths.maw(0)
    assert tths.read() == 0

    yield
    exp.finish()


def test_detector(session):
    adet = session.getDevice('adet')
    assert adet.liveinterval == 5

    tths = session.getDevice('tths')
    assert tths.speed == 0

    adet.reset()
    assert adet.read() == [1, 0, 0, 0]

    adet.liveinterval = 0.5
    assert adet.liveinterval == 0.5

    adet.resosteps = 2
    assert adet.resosteps == 2

    count(t=1)

    assert adet.range == 2
    assert adet._step_size == 1
    assert adet._startpos == 1
    assert adet._attached_motor.speed == 0
    assert adet._attached_motor.read(0) == 0

    adet.setPreset(t=0.5)
    adet.prepare()
    # The implementation of 'pause' and 'resume' command on MeasureSequencer
    # are missing at the moment
    # adet.start()
    # adet.pause()
    # adet.resume()

    count(resosteps=1, t=0.1)
    # Result should contain 4 elements
    assert len(adet.read()) == 4
    # Detector should be on the first reso step
    assert adet.read()[0] == 1

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

"""SPODI specific detector tests."""

from nicos.commands.measure import count

import pytest

session_setup = 'spodi'


@pytest.fixture(scope='class', autouse=True)
def prepare(session):
    """Prepare for SPODI tests"""

    session.experiment.new(0, user='user')

    # Check correct detector configuration
    basedet = session.getDevice('basedet')
    assert len(basedet._attached_timers) == 1
    assert len(basedet._attached_counters) == 0  #pylint: disable=len-as-condition
    assert len(basedet._attached_monitors) == 1
    assert len(basedet._attached_images) == 1
    adet = session.getDevice('adet')
    session.experiment.setDetectors([adet])
    assert session.experiment.detlist == ['adet']

    # Move the detector to a distinct position and check it
    tths = session.getDevice('tths')
    tths.maw(0)
    assert tths.read() == 0

    yield


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

    count(t=0.01)

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

    count(resosteps=1, t=0.01)
    # Result should contain 4 elements
    assert len(adet.read()) == 4
    # Detector should be on the first reso step
    assert adet.read()[0] == 1

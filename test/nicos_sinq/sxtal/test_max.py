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

import pytest

from nicos.core.utils import multiWait

from nicos_sinq.sxtal.commands import Center, Max

session_setup = 'sinq_sxtal'


@pytest.mark.parametrize('omstart', [
  2.9,
  1.,
  4.,
  0.,
  5.,
])
def test_max(session, omstart):
    om = session.getDevice('om')
    det = session.getDevice('det')
    session.experiment.setDetectors([det])

    om.start(omstart)
    multiWait([om])

    Max(om, .2, t=.05)

    assert(abs(om.read() - 3.0) < .05)


def test_max_away(session, log):
    om = session.getDevice('om')
    det = session.getDevice('det')
    session.experiment.setDetectors([det])

    om.start(20.)
    multiWait([om])

    with log.assert_errors(r'Peak out of range'):
        Max(om, .2, t=.05)


def test_center(session):
    motors = ('stt', 'om', 'chi', 'phi')
    positions = (12.0, 3.0, 44.5, 122.33)

    det = session.getDevice('det')
    session.experiment.setDetectors([det])
    sample = session.getDevice('Sample')
    rfl = sample.getRefList()
    rfl.clear()
    posoff = (positions[0]+1., positions[1]-1.,
              positions[2]+1., positions[3]-1)
    rfl.append((1, 0, 1), posoff, ())

    devs = []
    for mot in motors:
        devs.append(session.getDevice(mot))

    Center(0, t=.1)

    for mot, pos in zip(devs, positions):
        # Virtual counters in NICOS have an enormous jitter, this explains
        # the large tolerance.
        assert(abs(mot.read(0) - pos) < .3)

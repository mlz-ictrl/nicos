# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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


from nicos_sinq.icon.commands.iconcommands import tomo_run, tomo_setup

from test.utils import approx

session_setup = 'sinq_tomoscan'


def test_tomoscan(session, log):
    m = session.getDevice('motor2')
    det = session.getDevice('det')
    session.experiment.setDetectors([det])
    dataman = session.experiment.data

    # Simple test...
    det.setPreset(t=0.01)  # take images in finite time
    tomo_setup(m, 10)
    tomo_run()
    dataset = dataman.getLastScans()[-1]
    assert dataset.devvaluelists[0] == [1.0, 0.0]
    assert dataset.devvaluelists[1] == [2.0, 36.0]
    assert m.read() == approx(360, abs=0.02)

    # Run again
    tomo_run()
    dataset = dataman.getLastScans()[-1]
    assert dataset.devvaluelists[0] == [1.0, 0.0]
    assert dataset.devvaluelists[1] == [2.0, 36.0]
    assert m.read() == approx(360, abs=0.02)

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

session_setup = 'sinq_sxtal'


@pytest.mark.parametrize(('coneang', 'om', 'stt', 'chi', 'phi'), [
        (30, 7.622, 15.244, 142.239, 145.36),
        (60, 7.622, 15.244, 159.295, 131.035),
        (90, 7.622, 15.244, 180, 126.928)])
def test_cone(session, coneang, om, stt, chi, phi):
    # setting up
    s = session.getDevice('Sample')
    s.a = 6.28
    s.b = 6.28
    s.c = 6.28
    s.alpha = 90.
    s.beta = 90.
    s.gamma = 90.

    m = session.getDevice('mono')
    m.maw(1.178)

    cone = session.getDevice('cone')
    cone.center_reflection = ((1, 0, 0,), (5.382, 10.763, 180, 0))
    cone.target_reflection = (1, 1, 0)
    cone.qscale = 1.0

    omk = session.getDevice('om')
    sttk = session.getDevice('stt')
    chik = session.getDevice('chi')
    phik = session.getDevice('phi')

    cone.maw(coneang)
    assert abs(omk.read(0) - om) < .01
    assert abs(sttk.read(0) - stt) < .01
    assert abs(chik.read(0) - chi) < .01
    assert abs(phik.read(0) - phi) < .01

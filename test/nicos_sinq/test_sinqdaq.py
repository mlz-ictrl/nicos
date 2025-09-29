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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

from nicos.core.constants import SIMULATION


session_setup = 'sinq_daq'

def test_simulated_setup(session):
    # The purpose of this test is to check if all devices of SINQ DAQ can
    # created in simulation mode
    session._mode = SIMULATION
    _ = session.getDevice('ElapsedTime')
    _ = session.getDevice('DAQPreset')
    _ = session.getDevice('DAQ')
    _ = session.getDevice('ThresholdChannel')
    _ = session.getDevice('Threshold')
    _ = session.getDevice('Gate1')
    _ = session.getDevice('Gate2')
    _ = session.getDevice('TestGen')
    _ = session.getDevice('monitor1')
    _ = session.getDevice('monitor2')
    _ = session.getDevice('monitor3')
    _ = session.getDevice('monitor4')
    _ = session.getDevice('monitor5')
    _ = session.getDevice('monitor6')
    _ = session.getDevice('monitor7')
    _ = session.getDevice('monitor8')
    _ = session.getDevice('monitor9')
    _ = session.getDevice('monitor10')

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Stefan Mathis <stefan.mathis@psi.ch>
#   Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

"""AMOR specific commands and routines"""

import subprocess

from nicos import session
from nicos.commands import usercommand

@usercommand
def synchronize_daq():
    """Synchronize the time on the data acquisition computer with that of the
    ring modules.
    The local clocks on the ESS data acquisition PC and on the ring modules go
    quickly out of sync, which causes time offsets between the neutron signal
    and the proton current signal. To combat this, it is necessary to
    synchronize the clocks before each measurement with this command.
    """

    result = subprocess.run(
        ["ssh",
         "essdaq@amor-efu",
         "/home/essdaq/amor_tools/slow_control_driver/DetAndBM/correctTime.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        session.log.error('Synchronizing the DAQ time failed')
        session.log.error('Error: %s', result.stderr)

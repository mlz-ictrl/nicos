#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************
"""Special scan classes for AMOR"""

from __future__ import absolute_import, division, print_function

from nicos.core.scan import SweepScan


class WallTimeScan(SweepScan):
    """ Aligns counting at regular time intervals in order to facilitate
    correlation with external time controlled sample environment
    """

    def __init__(self, devices, startend, numpoints, walltime, firstmoves=None,
                 multistep=None, detlist=None, envlist=None, preset=None,
                 scaninfo=None, subscan=False):
        SweepScan.__init__(self, devices, startend, numpoints, firstmoves,
                           multistep, detlist, envlist, preset, scaninfo,
                           subscan)
        self.walltime = walltime

    def preparePoint(self, num, xvalues):
        SweepScan.preparePoint(self, num, xvalues)

        # Reset the preset depending on the elapsed time and expected time
        preset = num * self.walltime - self._etime.retrieve()
        if preset < 0:
            preset = 0
        self._preset = {'t': preset}

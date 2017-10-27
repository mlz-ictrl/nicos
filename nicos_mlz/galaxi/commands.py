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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#   L.Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

"""Module for GALAXI specific commands."""

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.commands.measure import count as nicos_count
from nicos_mlz.galaxi.devices.pilatus import PilatusDetector


@usercommand
@helparglist('number of rewrites, [presets]')
def count(num=1, **preset):
    """GALAXI specific command: Count with Pilatus detector and rewrite image"""

    exp = session.experiment
    preset['temporary'] = True
    for _ in range(num):
        for _det in exp.detectors:
            if isinstance(_det, PilatusDetector):
                _det.nextfilename = 'tmpcount.tif'
        nicos_count(**preset)
        # allow daemon to stop here
        session.breakpoint(2)

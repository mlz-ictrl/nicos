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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

"""Module for SANS-1 specific commands."""

from nicos import session
from nicos.commands import usercommand
from nicos.commands.measure import count
from nicos.commands.device import maw


__all__ = ['tcount']

@usercommand
def tcount(time_to_measure):
    """set the switch, fg1 and fg2 for tisane counts"""
    out_1 = session.getDevice('out_1')
    tisane_fg1_sample = session.getDevice('tisane_fg1_sample')
    tisane_fg2_det = session.getDevice('tisane_fg2_det')
    maw(out_1, 0)
    maw(tisane_fg1_sample, 'On')
    maw(tisane_fg2_det, 'On')

    maw(out_1, 1)
    count(time_to_measure)

    maw(out_1, 0)
    maw(tisane_fg1_sample, 'Off')
    maw(tisane_fg2_det, 'Off')

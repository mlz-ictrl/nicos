#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   NICOS measuring user commands
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Module for measuring user commands."""

__author__  = "$Author $"
__date__    = "$Date $"
__version__ = "$Revision $"

from time import sleep

from nicm import nicos
from nicm.commands import usercommand


def _count(detlist, preset):
    # put detectors in a set and discard them when completed
    detset = set(detlist)
    for det in detlist:
        det.start(**preset)
    while True:
        # XXX implement pause logic
        sleep(0.1)
        for det in list(detset):
            if det.isCompleted():
                detset.discard(det)
        if not detset:
            # all detectors finished measuring
            break
    return sum((det.read() for det in detlist), [])


@usercommand
def count(*detlist, **preset):
    """Perform a counting of the given detector(s) with the given preset(s)."""
    detlist = list(detlist)
    if detlist and isinstance(detlist[0], (int, long)):
        preset['t'] = detlist[0]
        del detlist[0]
    if not detlist:
        # XXX get default from Instrument or Experiment
        detlist = [nicos.getDevice('det')]
    _count(detlist, preset)

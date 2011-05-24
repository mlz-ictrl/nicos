#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Module for measuring user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from nicos import session
from nicos.device import Measurable
from nicos.errors import UsageError
from nicos.commands import usercommand


def _count(detlist, preset):
    # put detectors in a set and discard them when completed
    detset = set(detlist)
    for det in detlist:
        det.start(**preset)
    while True:
        # XXX implement pause logic
        sleep(0.025)
        for det in list(detset):
            if det.isCompleted():
                detset.discard(det)
        if not detset:
            # all detectors finished measuring
            break
    return sum((det.read() for det in detlist), ())


@usercommand
def count(*detlist, **preset):
    """Perform a counting of the given detector(s) with the given preset(s).

    Within a manual scan, perform the count as one step of the manual scan.
    """
    scan = getattr(session, '_manualscan', None)
    if scan is not None:
        if detlist:
            raise UsageError('cannot specify different detector list '
                             'in manual scan')
        scan.step(**preset)
        return
    detectors = []
    for det in detlist:
        if isinstance(det, (int, long, float)):
            preset['t'] = det
            continue
        if not isinstance(det, Measurable):
            raise UsageError('device %s is not a measurable device' % det)
        detectors.append(det)
    if not detectors:
        detectors = session.experiment.detectors
    return _count(detectors, preset)


@usercommand
def SetDetectors(*detlist):
    session.experiment.setDetectors(detlist)


@usercommand
def SetEnvironment(*devlist):
    session.experiment.setEnvironment(devlist)

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

import os

from nicos import session
from nicos.commands import usercommand
from nicos.core.errors import ConfigurationError
from nicos.utils import findResource


@usercommand
def loadcalibration():
    """
    Load CAMEA calibration files. Only needed in a new installation or
    after a modification of the calibration files.
    """
    dev = ['calib1', 'calib3', 'calib5', 'calib8']
    names = ['Normalization_1.calib', 'Normalization_3.calib',
             'Normalization_5.calib', 'Normalization_8.calib']
    for d, n in zip(dev, names):
        c = session.getDevice(d)
        c.load(findResource(os.path.join('nicos_sinq', 'camea', n)))


@usercommand
def SelectDetectorAnalyser(detNo, anaNo):
    """
    This command selects the detector and analyser to use for calculating
    counts in scans.
    """

    if detNo < 0 or detNo > 104:
        session.log.error('detNo %d out of range 0 - 104', detNo)
        return
    if anaNo < 0 or anaNo > 8:
        session.log.error('anaNo %d out of range 0 - 8', anaNo)
        return
    try:
        calib1 = session.getDevice('calib1')
        a4 = session.getDevice('a4')
        cts = session.getDevice('counts')
        efd = session.getDevice('ef')
        dn = session.getDevice('detNo')
        an = session.getDevice('anaNo')
    except ConfigurationError:
        session.log.error('Camea devices NOT found, cannot proceed')
        return

    idx = 8*detNo + anaNo
    a4offset = calib1.a4offset[idx]
    ef = calib1.energy[idx]
    anaMin = calib1.boundaries[idx*2]
    anaMax = calib1.boundaries[idx*2 + 1]
    a4.a4offset = a4offset
    # This order is implied by RectROIChannel.getReadResult()
    cts.roi = (anaMin, detNo, anaMax - anaMin, 1)
    dn.maw(detNo)
    an.maw(anaNo)
    session.log.info('Driving virtual ef to %f', ef)
    efd.maw(ef)

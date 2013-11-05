#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

from os import path

from nicos import session
from nicos.core import Measurable, Moveable
from nicos.core.spm import spmsyntax, Dev, Bare, Multi, Num
from nicos.commands import usercommand, helparglist
from nicos.commands.output import printinfo
from nicos.commands.measure import count
from nicos.commands.device import maw
from nicos.commands.scan import scan


@usercommand
@helparglist('[detectors], [presets]')
@spmsyntax(Multi(Dev(Measurable)), Bare)
def take_ob(*detlist, **preset):
    """Take an open beam image on the detector given as first argument.

    See `count()` for allowed arguments.
    """
    ccddevice = session.getDevice('ccd')
    exp = session.experiment
    oldmode = ccddevice.shuttermode
    try:
        ccddevice.shuttermode = 'auto'
        ccddevice.datapath = [exp.openbeampath]
        return count(*detlist, **preset)
    finally:
        ccddevice.shuttermode = oldmode

        lastImg = ccddevice.read(0)
        if lastImg:
            lastImg = path.basename(lastImg[0])
        else:
            lastImg = ''

        printinfo('last open beam image is %r' % lastImg)
        exp._setROParam('lastopenbeamimage', lastImg)
        ccddevice.datapath = exp.datapath


@usercommand
@helparglist('[detectors], [presets]')
@spmsyntax(Multi(Dev(Measurable)), Bare)
def take_di(*detlist, **preset):
    """Take an dark image on the detector given as first argument.

    See `count()` for allowed arguments.
    """
    ccddevice = session.getDevice('ccd')
    exp = session.experiment
    oldmode = ccddevice.shuttermode
    try:
        ccddevice.shuttermode = 'always_closed'
        ccddevice.datapath = [exp.darkimagepath]
        return count(*detlist, **preset)
    finally:
        ccddevice.shuttermode = oldmode

        lastImg = ccddevice.read(0)
        if lastImg:
            lastImg = path.basename(lastImg[0])
        else:
            lastImg = ''

        printinfo('last dark image is %r' % lastImg)
        exp._setROParam('lastdarkimage', lastImg)
        ccddevice.datapath = exp.datapath


@usercommand
@helparglist('n_angles, dev, [detectors], [presets]')
@spmsyntax(Num, Dev(Moveable),Multi(Dev(Measurable)), Bare)
def tomo(n_angles, dev=None, *detlist, **preset):
    """Performs a tomography by scanning over 360 deg in n_angles steps."""
    printinfo('Starting Tomography scan.')

    if dev is None:
        dev = session.getDevice('sry')

    stepwidth = 360.0 / n_angles

    printinfo('Acquiring 180 deg image first.')
    maw(dev, 180.0)
    count(*detlist, **preset)

    printinfo('Performing 360 deg scan.')
    scan(dev, 0, stepwidth, n_angles + 1, *detlist, **preset)

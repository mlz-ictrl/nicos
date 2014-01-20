#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Measurable
from nicos.core.spm import spmsyntax, Dev, Bare, Multi
from nicos.commands import usercommand, helparglist
from nicos.commands.output import printinfo
from nicos.commands.measure import count




@usercommand
@helparglist('[detectors], [presets]')
@spmsyntax(Multi(Dev(Measurable)), Bare)
def take_ob(*detlist, **preset):
    """Take an open beam image on the detector given as first argument. See `count()`."""
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

        printinfo('last openbeam image is %r' % lastImg)
        exp._setROParam('lastopenbeamimage', lastImg)
        ccddevice.datapath = exp.datapath

@usercommand
@helparglist('[detectors], [presets]')
@spmsyntax(Multi(Dev(Measurable)), Bare)
def take_di(*detlist, **preset):
    """Take an dark image on the detector given as first argument. See `count()`."""
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

        printinfo('last dark image is %r'% lastImg)
        exp._setROParam('lastdarkimage', lastImg)
        ccddevice.datapath = exp.datapath

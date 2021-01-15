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

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import maw
from nicos.commands.measure import count as std_count
from nicos.core.errors import ConfigurationError


@usercommand
@helparglist('None,on or off')
def sarot(op=None):
    motc = session.getDevice('motc')
    if op is None:
        res = int(motc.execute('ac 3'))
        if res == 0:
            return 'off'
        else:
            return 'on'
    elif op == 'on':
        motc.execute('ac 3 1')
        return 'ok'
    elif op == 'off':
        motc.execute('ac 3 0')
        return 'ok'
    else:
        session.log.error('Wrong argument to sarot: only inderstand None, on, off')

@usercommand
@helparglist('offset,divisor,length')
def UpdateHRPTBinning(offset,divisor,length):
    """Change the time binning for histogramming the data.

    This is for setting the proper parameters for the calculated stroboscopic
    axis at HRPT
    """
    # Get the configurator device
    try:
        configurator = session.getDevice('hm_configurator')
        bank = configurator.banks[0]
        strobo = bank.axes[1]
        strobo.length = length
        strobo.preoffset = offset
        strobo.divisor = divisor
        configurator.updateConfig()
    except ConfigurationError:
        session.log.error('The configurator device not found. Cannot proceed')



@usercommand
@helparglist('[detectors], [presets]')
def count(*detlist, **preset):
    try:
        racoll = session.getDevice('racoll')
    except ConfigurationError:
        racoll = None
    if racoll is None:
        session.log.warning('Radial collimator not found, skipping tests')
    else:
        if racoll.startcheck():
            maw(racoll,'on')

    std_count(*detlist,**preset)

    if racoll is not None:
        racoll.stopcheck()

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""AMOR specific commands and routines"""

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.core.errors import ConfigurationError

from nicos_sinq.amor.devices.hm_config import AmorTofArray


@usercommand
@helparglist('scheme, [value]')
def UpdateTimeBinning(scheme, value=None):
    """Changes the time binning for histogramming the data
    Time binning schemes:
        c/q/t <argument>
        c means Delta q / q = constant = <argument>
        q means Delta q = constant, <argument> is the number of bins/channels
        qq assumes two spectra per pulse
        t means Delta t = constant, <argument> is the number of bins/channels

    Example:

    Following command uses the scheme c with resolution of 0.005
    >>> UpdateTimeBinning('c', 0.005)

    Following command uses the scheme q with 250 channels
    >>> UpdateTimeBinning('q', 250)

    """
    # Get the configurator device
    try:
        configurator = session.getDevice('hm_configurator')
        for arr in configurator.arrays:
            if isinstance(arr, AmorTofArray):
                arr.applyBinScheme(scheme, value)
        configurator.updateConfig()
    except ConfigurationError:
        session.log.error('The configurator device not found. Cannot proceed')

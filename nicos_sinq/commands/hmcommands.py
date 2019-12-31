#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
"""
  This defines some general commands for handling PSI-SINQ histogram memories.
  It is mostly about maintaining the time binning.

"""
from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.core.errors import ConfigurationError

from nicos_sinq.devices.sinqhm.configurator import HistogramConfTofArray


@usercommand
@helparglist('start,step,count')
def UpdateTimeBinning(start, step, count):
    """Change the time binning for histogramming the data.

    This is the simple case of defining an equidistant time binning starting at
    start with count equidistant steps
    """
    # Get the configurator device
    try:
        configurator = session.getDevice('hm_configurator')
        for arr in configurator.arrays:
            if isinstance(arr, HistogramConfTofArray):
                arr.updateTimeBins(start, step, count)
        configurator.updateConfig()
    except ConfigurationError:
        session.log.error('The configurator device not found. Cannot proceed')


@usercommand
def ShowTimeBinning():
    """
    Shows the currently configured time binning
    """
    # Get the configurator device
    try:
        configurator = session.getDevice('hm_configurator')
        for arr in configurator.arrays:
            if isinstance(arr, HistogramConfTofArray):
                count = len(arr.data)
                step = arr.data[1] - arr.data[0]
                start = arr.data[0]
                session.log.info('Time Binning: start: %d, step %d, count = '
                                 '%d', start, step, count)
    except ConfigurationError:
        session.log.error('The configurator device not found. Cannot proceed')

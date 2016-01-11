#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Sans1 specific commands."""

from nicos import session
from nicos.core import ConfigurationError
from nicos.core.spm import spmsyntax, Int, String
from nicos.commands import usercommand, helparglist
from nicos.pycompat import string_types

from nicos.sans1.sans1_sample import Sans1Sample # pylint: disable=E0611,F0401


@usercommand
@helparglist('[index,] sample name')
@spmsyntax(Int, String) # how to tell spm?
def SetSample(idx, name = None):
    """Update sample name for given sample position in a samplechanger.

    This is a SANS1 specific command.

    Example:

    >>> SetSample('Probe')  # Sets name of sample 'Probe' if no samplechanger is used...
    >>> SetSample(2, 'Probe1')  # Sets name of sample in Location 2 to 'Probe1'

    If several sample names need to be specified, several calls to SetSample are
    required.
    """
    if name is None and isinstance(idx, string_types):
        idx, name = name, idx
    sd = session.experiment.sample   # get Sans1Sample device
    if not isinstance(sd, Sans1Sample):
        raise ConfigurationError("Instrument needs to be configured with a "
                                 "Sans1Sample for this command to work")
    sd.setName(idx, name)

@usercommand
@helparglist('')
@spmsyntax()
def ClearSamples():
    """Clears all samplenames.

    This is a SANS1 specific command.

    Example:

    >>> ClearSamples()
    """
    sd = session.experiment.sample   # get Sans1Sample device
    if not isinstance(sd, Sans1Sample):
        raise ConfigurationError("Instrument needs to be configured with a "
                                 "Sans1Sample for this command to work")
    sd.reset()

@usercommand
@helparglist('sampleposition')
@spmsyntax(int)
def SelectSample(pos):
    """Selects the sample at the given Sampleposition

    by selecting the right name and moving the samplechanger to the right position.

    This is a SANS1 specific command.

    Example:

    >>> SelectSample(3) # moves samplechanger to position 3

    """
    sd = session.experiment.sample   # get Sans1Sample device
    if not isinstance(sd, Sans1Sample):
        raise ConfigurationError("Instrument needs to be configured with a "
                                 "Sans1Sample for this command to work")
    c = session.getDevice('SampleChanger')
    c.maw(pos)
    if sd.activesample != pos: #was not updated by the samplechanger, so lets do it
        sd.activesample = pos


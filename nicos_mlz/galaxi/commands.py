#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""Module for GALAXI specific commands."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import basic, device, helparglist, measure, usercommand

from nicos_mlz.galaxi.devices.pilatus import PilatusDetector


@usercommand
@helparglist('proposal, title, localcontact, ...')
def NewExperiment(proposal, title='', localcontact='', user='', **parameters):
    """Start a new experiment with the given proposal number and title.

    You should also give a argument for the local contact and the primary user.
    More users can be added later with `AddUser`.  Example:

    >>> NewExperiment(541, 'Spin waves', 'L. Contact', 'F. User <user@abc.de>')

    When configured, proposal information will be automatically filled in from
    the proposal database.
    """
    if user:
        voice_output = session.getDevice('voice_output')
        device.move(voice_output, voice_output.read(0) ^ 1)
        session.log.info('Welcome to GALAXI, %s!', user)
    basic.NewExperiment(proposal, title, localcontact, user, **parameters)


@usercommand
@helparglist('[number of counts], [preset, ...]')
def count(n=1, **presets):
    """Perform *n* counts with all default detectors set with `SetDetectors()`.

    A temporary filename will be set when using DECTRIS Pilatus detector in
    order to be able to overwrite the TIFF images.

    Examples:

    >>> count()           # count once with the default preset and detectors
    >>> count(100)        # perform 100 counts without changing presets
    >>> count(t=10)       # count once with time preset of 10 seconds
    >>> count(10, t=60)  # perform 10 counts with time preset of 60 seconds

    :param int num: number of counts to be executed
    :param presets: presets to be used when counting
    """
    exp = session.experiment
    presets['temporary'] = True
    for _ in range(n):
        for _det in exp.detectors:
            if isinstance(_det, PilatusDetector):
                _det.nextfilename = 'tmpcount.tif'
        measure.count(**presets)
        session.breakpoint(2)  # allow daemon to stop here

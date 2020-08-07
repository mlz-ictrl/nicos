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
#
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""Module for GALAXI specific commands."""

from __future__ import absolute_import, division, print_function

from datetime import datetime
from os import path

from nicos import session
from nicos.commands import basic, device, helparglist, measure, usercommand
from nicos.core.constants import SCAN

from nicos_jcns.devices.pilatus_det import Detector as PilatusDetector, \
    TIFFImageSink as PilatusSink
from nicos_jcns.galaxi.devices.mythen_det import ImageSink as MythenSink


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
@helparglist('num_counts, [detectors], [presets]')
def count(n, *detlist, **presets):
    """Perform **n** counts while the TIFF image filename of the DECTRIS
    Pilatus detector will be set to a temporary value that remains unchanged
    during execution of this command.

    With preset arguments, this preset is used instead of the default preset.

    With detector devices as arguments, these detectors are used instead of the
    default detectors set with `SetDetectors()`.

    Examples:

    >>> # count 100 times without changing presets
    >>> count(100)
    >>>
    >>> # count 10 times and set the temporary filename to 'tmp.tif'
    >>> count(10, filename='tmp.tif')
    >>>
    >>> # count once with time preset of 10 seconds
    >>> count(1, t=10)

    Within a manual scan, this command is also used to perform the count as one
    point of the manual scan.
    """
    filename = presets.pop('filename', 'tmpcount.tif')
    galaxi_sinks = {sink: sink.settypes for sink in session.datasinks
                    if isinstance(sink, (MythenSink, PilatusSink))}
    try:
        for sink in galaxi_sinks:
            # deactivate during count
            sink._setROParam('settypes', [SCAN])
        for _ in range(n):
            for det in session.experiment.detectors:
                if isinstance(det, PilatusDetector):
                    det.imagedir = path.join(str(datetime.now().year),
                                             session.experiment.proposal)
                    det.nextfilename = filename
            measure.count(*detlist, **presets)
            session.breakpoint(2)  # allow daemon to stop here
    finally:
        for sink, settypes in galaxi_sinks.items():
            sink._setROParam('settypes', settypes)


@usercommand
@helparglist('radiation | (xray, threshold), [wait]')
def SetDetectorEnergy(radiation=None, **value):
    """For all default detectors set with `SetDetectors()` either load the
    predefined settings for that are suitable for usage with silver, chromium,
    copper, iron or molybdenum radiation or set the x-ray and threshold energy
    to any other appropriate values.

    The following keyword arguments are accepted:

      * *xray* -- x-ray energy in kilo electron volt
      * *threshold* -- threshold energy in kilo electron volt
      * *wait* -- whether the command should wait until all detectors
        completed the parameter update (defaults to 'True')

    Examples:

    >>> # load predefined settings for copper radiation
    >>> SetDetectorEnergy('Cu')
    >>>
    >>> # set energy values explicitly
    >>> SetDetectorEnergy(xray= 9.243, threshold= 8.0)
    >>>
    >>> # load predefined settings for silver radiation and return immediately
    >>> SetDetectorEnergy('Ag', wait=False)
    """
    wait = value.pop('wait', True)
    configured = []
    for det in session.experiment.detectors:
        for ch in det._channels:
            if hasattr(ch, 'setEnergy'):
                configured.append(det)
                ch.setEnergy(radiation, **value)
                break  # maximum one channel per detector can set energy
    if wait:
        device.wait(*configured)

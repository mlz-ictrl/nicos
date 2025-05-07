# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

from datetime import datetime
from os import path

from nicos import session
from nicos.commands import basic, device, helparglist, measure, usercommand
from nicos.core.constants import SCAN
from nicos.devices.datasinks.tiff import TIFFImageSink
from nicos.protocols.daemon import BREAK_AFTER_STEP

from nicos_jcns.devices.dectris import Detector2D as DECTRIS2DDetector, \
    FileSink as DECTRIS2DFileSink, MYTHENImageSink


@usercommand
@helparglist('proposal, [title, localcontact, user, ...]')
def NewExperiment(proposal, title='', localcontact='', user='', **parameters):
    """Start a new experiment with the given proposal number and title.

    You should also give an argument for the local contact and the primary user.
    More users can be added later with `AddUser`.  Example:

    >>> NewExperiment(541, 'Spin waves', 'L. Contact', 'F. User <user@abc.de>')

    When configured, proposal information will be automatically filled in from
    the proposal database.

    see also: `FinishExperiment`
    """
    if user:
        voice_output = session.getDevice('voice_output')
        device.move(voice_output, voice_output.read(0) ^ 1)
        session.log.info('Welcome to GALAXI, %s!', user)
    basic.NewExperiment(proposal, title, localcontact, user, **parameters)


@usercommand
@helparglist('num_counts, [detectors], [presets]')
def count(n, *detlist, **presets):
    """Perform **n** counts while the image filename of the currently active
    DECTRIS detectors will be set to a temporary value that remains unchanged
    during execution of this command.

    With preset arguments, this preset is used instead of the default preset.

    With detector devices as arguments, these detectors are used instead of the
    default detectors set with `SetDetectors()`.

    Examples:

    >>> # count 100 times without changing presets
    >>> count(100)
    >>>
    >>> # count 10 times and set the temporary filename to 'tmp'
    >>> count(10, filename='tmp')
    >>>
    >>> # count once with time preset of 10 seconds
    >>> count(1, t=10)

    Within a manual scan, this command is also used to perform the count as one
    point of the manual scan.
    """
    filename = presets.pop('filename', 'tmpcount')
    galaxi_sinks = {sink: sink.settypes for sink in session.datasinks
                    if isinstance(sink, (MYTHENImageSink, DECTRIS2DFileSink,
                                         TIFFImageSink))}
    try:
        for sink in galaxi_sinks:
            sink._setROParam('settypes', [SCAN])  # deactivate during count
        for _ in range(n):
            for det in session.experiment.detectors:
                if isinstance(det, DECTRIS2DDetector):
                    det.nextimagepath = path.join(str(datetime.now().year),
                                                  session.experiment.proposal,
                                                  filename)
            measure.count(*detlist, **presets)
            session.breakpoint(BREAK_AFTER_STEP)  # allow daemon to stop here
    finally:
        for sink, settypes in galaxi_sinks.items():
            sink._setROParam('settypes', settypes)


@usercommand
@helparglist('element | (photon_energy, threshold_energy), [wait]')
def SetDetectorEnergy(element=None, **value):
    """For all default detectors in ``session.experiment.detectors`` either set
    the energy parameters to the K-alpha fluorescence radiation energy of an
    element or set the photon and threshold energy to any other appropriate
    values.

    The following keyword arguments are accepted:

      * *photon* -- photon energy in kilo electron volt
      * *threshold* -- threshold energy in kilo electron volt
      * *wait* -- whether the command should wait until all detectors
        completed the parameter update (defaults to `True`)

    Examples:

    >>> # load predefined settings for copper radiation
    >>> SetDetectorEnergy('Cu')
    >>>
    >>> # set energy values explicitly
    >>> SetDetectorEnergy(photon=9.243, threshold=8.0)
    >>> SetDetectorEnergy(photon=9.243, threshold=[8.0, 10.0])
    >>>
    >>> # load predefined settings for silver radiation and return immediately
    >>> SetDetectorEnergy('Ag', wait=False)
    """
    wait = value.pop('wait', True)
    configured = []
    for det_name in session.experiment.detectors:
        det = session.getDevice(det_name)
        if hasattr(det, 'setEnergy'):
            det.setEnergy(element, **value)
            configured.append(det)
    if wait:
        device.wait(*configured)
        for det in configured:
            det.poll()  # show updated energy value

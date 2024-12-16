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
#   Christine Klauser <christine.klauser@psi.ch>
#   Jose Gomez <Jose.Gomez@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.analyze import gauss, sigmoid
from nicos.commands.device import adjust, maw
from nicos.commands.sample import NewSample
from nicos.commands.scan import cscan, scan
from nicos.core.errors import ConfigurationError, UsageError
from nicos.devices.epics.pyepics.motor import EpicsMotor

from nicos_sinq.devices.lin2ang import Lin2Ang

__all__ = ['AlignAndMeasure']


@usercommand
@helparglist('samplename, thickness, mvalue, measure [, stepwidth=0.02,' +
             ' startsom=0, countstotalrefl=1.2e4, scancounts=3e4,' +
             ' offsetstyscan=2, pointsbeyondm=16]')
def AlignAndMeasure(  # pylint: disable=too-many-positional-arguments
        samplename, thickness, mvalue, measure, stepwidth=0.02,
        startsom=0, countstotalrefl=1.2e4, scancounts=3e4, offsetstyscan=2,
        pointsbeyondm=16):
    """Aligns a non-polarized mirror on the NARZISS beamline and measures
    the reflectivity

             Bulk
           |-------| (where total reflection occurs)
            region

           ▲
           │
           │
           │
           │........
           │       ....
       I   │          ....
           │             ...
    (ctr1) │               .
           │               ..
           │                ..
           │                 .......
           └────────────────────────►

                    θ(som)

    Supported parameters are the following:
    * ``samplename``: name of the new sample to measure
    * ``thickness``: substrate thickness in millimetres
    * ``mvalue``: sample m-value
    * ``measure``: if ``True``, execute measurement after adjustment.
                   ``countstotalrefl`` has no effect if this is ``False``
    * ``stepwidth=0.02``: distance between each scan point
    * ``startsom=0``: first angle at which to scan
    * ``countstotalrefl=1.2e4``: how many counts are needed in area of
                                 total reflection
    * ``scancounts=3e4``: number of neutron events that should be registered
                          at each scan point
                          should be adjusted for slit sizes smaller than
                          0.8/50, 0.6/30, 5/30, 10/50
    * ``offsetstyscan=2``: offset in mm from sample thickness to start scan
                           during alignment
    * ``pointsbeyondm=16``: number of points to scan after the m-value

    Examples::

        AlignAndMeasure('MyShinySample', 11, 3, 1)
    """

    # Ensure required devices exist
    try:
        som = session.getDevice('som', cls=EpicsMotor)
        stt = session.getDevice('stt', cls=Lin2Ang)
        sty = session.getDevice('sty', cls=EpicsMotor)
    except ConfigurationError as exc:
        raise UsageError('The setups containing the devices som, stt and' +
                         ' sty must be loaded to use this function.') from exc

    # roughly som_position * 2 = mvalue(=stt position)
    nopoints = round(mvalue / 2 / stepwidth) -\
        round(startsom / 2 * stepwidth) + pointsbeyondm

    startsty = thickness + offsetstyscan

    if mvalue >= 2:
        t2t = 2
    else:
        t2t = 1

    # Alignment
    NewSample(samplename)
    maw(som, 0, stt, 0, sty, 0)

    maxcounts = 0
    delta_theta = 1

    session.log.info('Starting Alignment')
    while delta_theta > 0.005:
        maw(som, 0, stt, 0)
        scan(sty, startsty, -0.1, 41, m=scancounts)
        pos = sigmoid('sty', 'ctr1')

        maxcounts = pos[0][0]
        maw(sty, pos[0][2])
        maw(stt, t2t)
        cscan(som, t2t / 2, 0.02, 13, m=scancounts * 1.5)
        values = gauss('som', 'ctr1')
        center_g = values[0][0]
        delta_theta = abs(center_g - t2t / 2)
        adjust(som, center_g, t2t / 2)

    session.log.info('Alignment Complete')

    # Measurement
    if measure:
        session.log.info('Starting Measurement: Scanning %s points', nopoints)

        ncounts = round(countstotalrefl / maxcounts * scancounts, -3)

        scan([som, stt],
             [startsom, 2 * startsom],
             [stepwidth, 2 * stepwidth],
             nopoints,
             m=ncounts)

        maw(som, 0, stt, 0, sty, 0)

        session.log.info('Measurement Complete')
    else:
        session.log.info('Skipping Measurement')

#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""STRESS-SPEC specific commands for the robot to change the sample."""

import numpy

from nicos import session
from nicos.core.errors import PositionError
from nicos.commands import usercommand, helparglist
from nicos.commands.basic import sleep
from nicos.commands.device import maw
from nicos.commands.scan import contscan

__all__ = (
    'gauge_to_base', 'base_to_gauge', 'set_sample', 'pole_figure',
    'change_sample'
)


def move_dev(dev, pos, sleeptime=0, maxtries=3):
    session.log.info('Moving %s to %f', dev, pos)
    d = session.getDevice(dev)
    for _ in range(maxtries):
        d.maw(pos)
        if sleeptime:
            sleep(sleeptime)
        if abs(d.read() - pos) < d.precision:
            return
    raise PositionError(dev, 'Could not move %d to %f' % (dev, pos))


@usercommand
@helparglist('')
def gauge_to_base():
    session.getDevice('phis').speed = 2 * 50
    session.getDevice('xt').speed = 2 * 40
    dev_pos = [('robt', 13),

               ('zt', -400), ('robj3', -1), ('robj1', -1),
               ('robj2', -2), ('robj3', -110),

               ('zt', 140), ('chis', 190), ('robb', -2), ('phis', 10),
               ('yt', 610), ('xt', -515)]

    for dev, pos in dev_pos:
        move_dev(dev, pos)  # or sleeptime=5
    session.log.info('Base reached')
    session.getDevice('phis').speed = 50
    session.getDevice('xt').speed = 40


@usercommand
@helparglist('toolnumber')
def base_to_gauge(tool):
    """Move from the base position to the measurement position 'toolnumber'.

    Examples::

        # Move to measurement position 1
        >>> base_to_gauge(1)
    """
    session.getDevice('phis').speed = 2 * 50
    session.getDevice('xt').speed = 2 * 40
    # omgr in robot software offset must be <= -10
    dev_pos = [('zt', -200), ('robj3', -1),
               ('robj1', -70), ('robj3', -100), ('xt', 0),
               ]
    for dev, pos in dev_pos:
        move_dev(dev, pos)  # or sleeptime=7

    # select tool (gauge volume)
    move_dev('robt', tool, maxtries=1)

    # move to gauge center
    move_dev('chis', 180.)

    session.getDevice('xt').speed = 40
    for dev in ['robb', 'phis', 'zt', 'xt', 'yt']:
        move_dev(dev, 0)  # or sleeptime=5
    session.log.info('Tool %d reached', tool)
    session.getDevice('phis').speed = 50


@usercommand
@helparglist('samplenumber')
def set_sample(sample):
    # the CARESS device give pos 0 during movement, which confuses the axis
    # code if the position is moving up
    move_dev('robs', 0, maxtries=1)
    move_dev('robs', int(sample), maxtries=1)
    session.log.info('Sample %d got', int(sample))


@usercommand
@helparglist('numrows, speed, timedelta, sampleinfo')
def pole_figure(numrows, speed, timedelta, sampleinfo):
    """Run a typical pole figure measurement.

    The command runs 'numrows' continuous scans over the 'phis' device, which
    makes a full turn (360 deg) during the measurement.

    The changed parameter device is 'chis'. It divides the angle of 90 deg into
    'numrows' steps, starting at the half of the stepsize. A 'numrows' of 6
    will generate the 'chis' positions of 172.5, 157.5, 142.5, 127.5, 112.5,
    and 97.5 deg.

    Examples::

        # create a pole figure measurement with 6 steps taking every 10 s a
        # picture
        >>> pole_figure(6, 0.25, 10, 'Alpha_Ti')

    """
    chis = session.getDevice('chis')
    phis = session.getDevice('phis')
    dchi = round(90.0 / numrows, 2) / 2.0
    # creating a list beginnig from 180 + dchi downsteps to 90 + dchi
    positions = numpy.arange(90 + dchi, 180, 2 * dchi)[::-1]
    maw(phis, 0)
    for i, chipos in enumerate(positions):
        move_dev(chis, round(chipos, 2), maxtries=2)
        sleep(5)
        start, end = (360., 0.) if i % 2 else (0., 360.)
        contscan(phis, start, end, speed, timedelta,
                 '%s_Chis_%s' % (sampleinfo, str(chis.read())))
    sleep(5)
    maw(phis, 0)
    sleep(5)
    maw(chis, 180)
    sleep(5)


@usercommand
def change_sample(samplenr, toolnr=None):
    """Change the sample with the help of the robot.

    The robot moves the current sample into the sample holder magazine, takes
    the sample 'samplenr', and move the sample into the measuring position
    'toolnr'. The 'toolnr' (tool number) specifies the position inside the
    sample.
    If the 'toolnr' is not given it will the taken the 'samplenr' as 'toolnr'.
    If the 'samplenr' is 0 then the current sample will be put into the
    magazine

    Examples::

        # put the current sample into the sample magazine and take the sample
        # 3 into measuring position 2
        >>> change_sample(3, 2)

        # put the current sample into the sample magazine and put the sample 1
        # into measuring position 1
        >>> change_sample(1)

        # put the current sample into the sample magazine and move the robot
        # into measuring position 1 without any sample
        >>> change_sample(0)
    """
    if toolnr is None:
        toolnr = samplenr if samplenr else 1
    # From beam center to slot
    gauge_to_base()
    # Select sample
    set_sample(samplenr)
    # From slot to beam center
    base_to_gauge(toolnr)

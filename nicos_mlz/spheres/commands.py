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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

"""Custom commands for SPHERES"""

from __future__ import absolute_import, division, print_function

from nicos.commands import parallel_safe, usercommand
from nicos.commands.device import maw
from nicos.core import UsageError
from nicos.utils import parseDuration as pd

from nicos_mlz.spheres.devices.doppler import INELASTIC
from nicos_mlz.spheres.utils import getDoppler, getSisImageDevice, \
    getTemperatureController, parseDuration, waitForAcq


@usercommand
def changeDopplerSpeed(target):
    """Change the doppler speed to the specified speed.
    Only the predefined values in the doppler setup are allowed."""

    doppler = getDoppler()

    if waitForAcq():
        maw(doppler, target)
    else:
        raise UsageError('Detector is busy. Therefore the doppler speed can '
                         'not be changed.')


@usercommand
def setStick(value):
    """Adjust the Hardware to use the selected stick"""

    if value not in ('ht', 'lt'):
        raise UsageError('Value must be either "ht" for the high temperature'
                         ' or "lt" for the low temperature stick.')
    getTemperatureController().SetActiveStick(value)


@usercommand
def ramp(target, ramp=None):
    """Move the temperature to target with the given ramp.
    If ramp is omitted and the current ramp is > 0 it is used.
    If the current ramp is 0 the command is not executed.
    """

    controller = getTemperatureController()

    if ramp is not None:
        if ramp > 100:
            raise UsageError('TemperatureController does not support ramps '
                             'higher then 100 K/min. If you want to get to '
                             '%f as fast as possible use rush(%f). '
                             'Ramp will be set to max.' % (target, target))
        controller.ramp = ramp
    elif controller.ramp == 0:
        raise UsageError('Ramp of the TemperatureController is 0. '
                         'Please specify a ramp with this command.\n'
                         'Use "ramp(target, RAMP)", '
                         '"timeramp(target, time)", or "rush(target)"')

    controller.move(target)


@usercommand
def timeramp(target, time):
    """Ramp to the given target in the given timeframe.
    Ramp will be calculated by taking current temperature, given target and
    given time into account. Ramps for tube and sample will be calculated
    separately"""

    time = parseDuration(time, 'timeramp')

    controller = getTemperatureController()

    # stop current ramp
    controller.ramp = 0
    controller.move(controller.read())

    # set new target
    controller.ramp = abs(target-controller.read())/(time/60)
    controller.move(target)


@usercommand
def rush(target):
    """Move to the given temperature as fast as possible.
    Previously set ramps will be ignored but preserved.
    """

    getTemperatureController().rushTemperature(target)


@usercommand
def stoppressure():
    """Stop pressure regulation"""

    getTemperatureController().stopPressure()


@usercommand
def stoptemperature():
    """Stop the temperature ramp"""

    controller = getTemperatureController()
    old_ramp = controller.ramp

    controller.ramp = 0
    controller.move(controller.read())
    controller.ramp = old_ramp


@parallel_safe
@usercommand
def showDetectorSettings():
    """Print the current detector settings.
    Prints the currently set measure mode and parameters.
    """
    image = getSisImageDevice()
    if not image:
        return

    mode = image.getMode()

    if mode == INELASTIC:
        print('SIS detector is measuring inelastic.',
              'Counttime per file: %s'
              % pd(image.inelasticinterval))
    else:
        params = image.elasticparams
        print('The SIS detector is measuring elastic.',
              'Lines per file: %d' % params[0],
              'Counttime per line: %s' % pd(params[1]),
              'Counttime per file: %s' % pd(params[0]*params[1]))

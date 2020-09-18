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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

"""Custom commands for SPHERES"""

from nicos.commands import usercommand
from nicos.core import UsageError

from nicos_mlz.spheres.utils import getTemperatureController, parseDuration


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

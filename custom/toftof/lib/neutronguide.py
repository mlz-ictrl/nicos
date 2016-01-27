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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF neutron guide/collimator switcher device."""

from nicos.core import Param, Override, NicosError, intrange
from nicos.devices.abstract import CanReference
from nicos.devices.generic import Switcher as GenericSwitcher
from nicos.core.params import Attach
from nicos.devices.taco import Motor as TacoMotor, DigitalInput


class Switcher(GenericSwitcher):
    """
    Switcher, specially adopted to TOFTOF needs

    The neutron guide switcher has two different guides and the job is to
    change between them. Since there is no encoder mounted to check the
    position each change has to start with a reference move, followed by
    the move to the target position.
    """

    parameter_overrides = {
        'precision':    Override(default=0.1, mandatory=False),
        'fallback':     Override(default='Unknown', mandatory=False),
        'blockingmove': Override(default='False', mandatory=False),
    }

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        if isinstance(self._attached_moveable, CanReference):
            self.log.info('referencing %s...' % self._attached_moveable)
            self._attached_moveable.reference()
        else:
            self.log.warning('%s cannot be referenced!' %
                             self._attached_moveable)
        self._attached_moveable.start(target)
        if self.blockingmove:
            self._attached_moveable.wait()


class Motor(TacoMotor):
    """
    These devices move the neutron guide blades of the focussing neutron
    guide via the connected piezo motor. Since there is no encoder mounted
    and the positioning is very strongly depending on the bending force of
    the glass blade each positioning must be start with a referencing task.
    The reference task moves the motor in a position that the 'limit switch'
    is activated, followed by stepwise move backwards until the 'limit switch'
    is deactivated.
    The used controller has no input for a limit switch.
    """

    parameters = {
        'refspeed': Param('Reference speed',
                          type=float, default=500, settable=False,),
        'refpos':   Param('Reference position',
                          type=float, default=0, settable=False,),
        'refstep': Param('Number of steps to move to reference position',
                         type=intrange(1, 100), default=10, settable=False,),
    }

    attached_devices = {
        'limitsw': Attach('Lower limit switch device', DigitalInput),
    }

    def doStart(self, target):
        self.doReference()
        TacoMotor.doStart(self, target)

    def _stepping_until(self, start, step, switch):
        self.log.debug('Set position : %d' % (start))
        self.doSetPosition(start)
        while self._attached_limitsw.read(0) == switch:
            start += step
            TacoMotor.doStart(self, start)
        self.wait()

    def doReference(self):
        # first set the position to the max position
        # move in steps to the min position until the limit switch is reached
        # move in steps until the limit switch is left
        # set the position to 0
        if self._attached_limitsw.read(0) == 1:
            self._stepping_until(self.absmax, -100, 1)
        try:
            speed = self.speed
            self.speed = self.refspeed
            self._stepping_until(self.absmin, self.refstep, 0)
            self.doSetPosition(self.refpos)
            self.log.info('Referenced to : %.2f' % self.refpos)
        except NicosError as err:
            self.log.debug('exception in referencing : %s' % err)
        finally:
            self.speed = speed

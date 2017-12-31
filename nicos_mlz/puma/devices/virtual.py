#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
"""PUMA specific virtual devices."""

from nicos import session
from nicos.core import Attach, Moveable, Override, Param, intrange, none_or, \
    status
from nicos.core.errors import UsageError
from nicos.devices.abstract import CanReference
from nicos.devices.generic import VirtualMotor
from nicos.pycompat import string_types


class VirtualReferenceMotor(CanReference, VirtualMotor):
    """Virtual motor device with reference capability."""

    parameters = {
        'refpos': Param('Reference position if given',
                        type=none_or(float), settable=False, default=None,
                        unit='main'),
        'addr': Param('Bus address of the motor', type=intrange(32, 255),
                      default=71),
    }

    def doReference(self, *args):
        refswitch = args[0] if args and isinstance(args[0], string_types) \
            else None
        self.log.debug('reference: %s', refswitch)
        self._setrefcounter()
        if self.refpos is not None:
            ret = self.read(0)
            self.log.debug('%s %r', self.name, self.isAtReference())
            return ret
        return self.refpos

    def _setrefcounter(self):
        self.log.debug('in setrefcounter')
        if self.refpos is not None:
            self.setPosition(self.refpos)
            self._setROParam('target', self.refpos)
            self.log.debug('%r %r', self.refpos, self.target)
            session.delay(0.1)
        if not self.isAtReference():
            raise UsageError('cannot set reference counter, not at reference '
                             'point')

    def isAtReference(self, refswitch=None):
        if self.refpos is None:
            return False
        pos = self.read(0)
        is_at_refpos = abs(self.refpos - self.read(0)) <= self.precision
        if refswitch == 'low':
            return is_at_refpos and (abs(self.abslimits[0] - pos) <
                                     abs(self.abslimits[1] - pos))
        elif refswitch == 'high':
            return is_at_refpos and (abs(self.abslimits[0] - pos) >
                                     abs(self.abslimits[1] - pos))
        return is_at_refpos


class DigitalInput(Moveable):
    """A test DigitalInput."""

    parameters = {
        '_value': Param('Simulated value',
                        type=intrange(0, 0xFFFFFFFF), default=0,
                        settable=False, userparam=False,),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, settable=False, default=''),
        'fmtstr': Override(default='%d'),
    }

    valuetype = intrange(0, 0xFFFFFFFF)

    def doRead(self, maxage=0):
        return self._value

    def doStatus(self, maxage=0):
        return status.OK, 'idle'


class LogoFeedBack(DigitalInput):
    """Device to simulate the LOGO feed back."""
    attached_devices = {
        'input': Attach('Digital input device', DigitalInput),
    }

    def doRead(self, maxage=0):
        v = self._attached_input.read(maxage)
        return sum((0x2 | min(1, ((1 << i) & v))) << (2 * i)
                   for i in range(8))


class DigitalOutput(DigitalInput):
    """A test DigitalOutput."""

    def doStart(self, target):
        self._setROParam('_value', target)

# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
"""Radial collimator devices."""

from nicos.core import status
from nicos.core.device import Moveable
from nicos.core.errors import InvalidValueError
from nicos.core.params import Attach, Override, Param, floatrange, limits, \
    oneof
from nicos.devices.entangle import Motor


class RadialCollimator(Moveable):

    valuetype = oneof('on', 'off')

    attached_devices = {
        'motor': Attach('Motor driving the radial collimator', Motor)
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False, settable=False),
    }

    parameters = {
        'frequency': Param('Frequency of oscillation',
                           type=floatrange(0), unit='Hz', settable=True,
                           userparam=True, category='instrument'),
        'frequency_limits': Param('The frequency limits',
                                  type=limits, unit='Hz', settable=False,
                                  volatile=True),
    }

    def doStatus(self, maxage=0):
        st, msg = self._attached_motor.status(maxage)
        if st in [status.OK, status.BUSY]:
            return status.OK, msg
        return status.ERROR, msg

    def doRead(self, maxage=0):
        return 'on' if self._attached_motor.status(maxage)[0] == status.BUSY \
            else 'off'

    def doReadFrequency_Limits(self):
        return (float(self._attached_motor._getProperty('minspeed')) / 360,
                float(self._attached_motor._getProperty('maxspeed')) / 360)

    def doStart(self, target):
        if target == 'off':
            self._attached_motor.stop()
        else:
            try:
                floatrange(*self.frequency_limits)(self.frequency)
            except ValueError as err:
                raise InvalidValueError(
                    self, '%r is an invalid value for parameter %s: %s' % (
                        self.frequency, 'frequency', err)) from err
            self._attached_motor._dev.MoveCont(360 * self.frequency)

    def doReadUnit(self):
        return ''

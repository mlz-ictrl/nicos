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

"""NICOS pulse device."""

from nicos.core import Attach, Moveable, Param, anytype, oneof
from nicos.core.errors import ConfigurationError

from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep


class Pulse(BaseSequencer):
    """The device generates a 'trigger' signal.

    The device switches the attached device into the 'on' state (moving
    attached device to 'onvalue') for 'ontime' seconds and switches the it back
    to 'offvalue' after the 'ontime'.
    """

    parameters = {
        'onvalue': Param("Value of the attached 'switch' considered to be as "
                         "'on'",
                         type=anytype, settable=False, userparam=False,
                         mandatory=True,
                         ),
        'offvalue': Param("Value of the attached 'switch' considered to be as "
                          "'off'",
                          type=anytype, settable=False, userparam=False,
                          mandatory=True,
                          ),
        'ontime': Param('Time to stay at "on" value',
                        type=float, settable=False, userparam=True,
                        mandatory=True, unit='s',
                        ),
    }

    attached_devices = {
        'moveable': Attach('Device performing the trigger signal', Moveable),
    }

    hardware_access = False

    def doInit(self, mode):
        if not self._attached_moveable.isAllowed(self.onvalue)[0]:
            raise ConfigurationError(self, "'onvalue' is not allowed for the "
                                     "'%s' device" % self._attached_moveable)
        if not self._attached_moveable.isAllowed(self.offvalue)[0]:
            raise ConfigurationError(self, "'offvalue' is not allowed for the "
                                     "'%s' device" % self._attached_moveable)
        self.valuetype = oneof(self.offvalue, self.onvalue)

    def doStart(self, target):
        if self._seq_is_running():
            self.stop()
            self.log.info('waiting for trigger to stop...')
            self._hw_wait()
            self._seq_thread.join()
            self._seq_thread = None
        self._startSequence(self._generateSequence(target))

    def doRead(self, maxage=0):
        return self.onvalue if self._seq_is_running() else self.offvalue

    def _generateSequence(self, target):  # pylint: disable=W0221
        seq = []
        if target == self.onvalue:
            seq.append(SeqDev(self._attached_moveable, self.onvalue))
            seq.append(SeqSleep(self.ontime))
        seq.append(SeqDev(self._attached_moveable, self.offvalue))
        return seq

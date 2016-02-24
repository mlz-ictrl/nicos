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

"""Shutter button simulation devices."""

from nicos.core import Attach, Param, Moveable, Readable, floatrange

from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqDev, SeqSleep


class Button(BaseSequencer, Moveable):
    """The Button class emulates the pressing of an real button at the hardware
    by a human.  This means the value will be set to an 'on' state the human
    presses the button down, wait some time and then setting the value to an
    'off' state, the human releases the button.

    """
    attached_devices = {
        'switch': Attach('The I/O device which is controlled',
                         Moveable),
        'feedback': Attach('An optional feedback to check the triggered state',
                           Readable, optional=True),
    }

    parameters = {
        'delay': Param('Time where the button is pressed (in ms)',
                       type=floatrange(0.001, 10), default=0.1),
    }

    def _generateSequence(self, target):  # pylint: disable=W0221
        return [
            SeqDev(self._attached_switch, 1),
            SeqSleep(self.delay),
            SeqDev(self._attached_switch, 0),
        ]

    def doStart(self, target):
        if self._seq_is_running():
            self.log.info('waiting for button to stop...')
            self.wait()
        self._startSequence(self._generateSequence(target))

    def doRead(self, maxage=0):
        if self._attached_feedback:
            return self._attached_feedback.read(maxage)
        return self._attached_switch.read(maxage)
